from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from populate_core.models import AccessPolicy
from users.models import Role
from feed.models import FeedGroup, FeedChannel, FeedPost, FeedComment, TeamMessage

User = get_user_model()


class FeedCollaborationTestCase(TestCase):
    def setUp(self):
        self.role_emp, _ = Role.objects.get_or_create(name="Employee", defaults={"is_superadmin": False})

        for model_name in ["feed_group", "feed_channel", "feed_post", "feed_comment", "team_message"]:
            AccessPolicy.objects.get_or_create(
                role=self.role_emp,
                model_name=model_name,
                defaults={
                    "actions": ["read", "create", "update", "delete"],
                    "allow_access": {"read": ["*"], "create": ["*"], "update": ["*"], "delete": ["*"]},
                    "status": 1
                }
            )

        self.admin_user, _ = User.objects.get_or_create(username="admin_test", defaults={"email": "admin@example.com", "is_superuser": True})
        self.alice, _ = User.objects.get_or_create(username="alice", defaults={"email": "alice@example.com", "role": self.role_emp})
        self.bob, _ = User.objects.get_or_create(username="bob", defaults={"email": "bob@example.com", "role": self.role_emp})
        self.charlie, _ = User.objects.get_or_create(username="charlie", defaults={"email": "charlie@example.com", "role": self.role_emp})

        self.client = APIClient()

    def test_full_feed_and_collaboration_lifecycle(self):
        # 1. Feed Group & Auto-Membership
        self.client.force_authenticate(user=self.alice)
        res_group = self.client.post("/api/populate/create/feed_group/", {"name": "Frontend Guild"}, format="json")
        self.assertEqual(res_group.status_code, 201)
        group_item = res_group.data["data"]
        group_id = group_item[0]["id"] if isinstance(group_item, list) else group_item["id"]
        group = FeedGroup.objects.get(id=group_id)
        self.assertTrue(group.members.filter(id=self.alice.id).exists())

        # 2. Feed Channel
        res_channel = self.client.post("/api/populate/create/feed_channel/", {"name": "react-general", "is_external": False}, format="json")
        self.assertEqual(res_channel.status_code, 201)
        channel_item = res_channel.data["data"]
        channel_id = channel_item[0]["id"] if isinstance(channel_item, list) else channel_item["id"]
        channel = FeedChannel.objects.get(id=channel_id)
        self.assertTrue(channel.members.filter(id=self.alice.id).exists())
        channel.members.add(self.bob)

        # 3. Anti-Spoofing on FeedPost
        res_spoof = self.client.post("/api/populate/create/feed_post/", {
            "content": "I am pretending to be Bob",
            "author": self.bob.id,
            "channel": channel_id
        }, format="json")
        self.assertIn(res_spoof.status_code, (400, 403))

        # 4. Legitimate FeedPost
        res_post = self.client.post("/api/populate/create/feed_post/", {
            "content": "Welcome to React General! Please check guidelines.",
            "subject": "Kickoff Meeting",
            "channel": channel_id,
            "post_type": "Announcement"
        }, format="json")
        self.assertEqual(res_post.status_code, 201)
        post_item = res_post.data["data"]
        post_id = post_item[0]["id"] if isinstance(post_item, list) else post_item["id"]
        post = FeedPost.objects.get(id=post_id)
        self.assertEqual(post.author_id, self.alice.id)
        self.assertTrue(post.followers.filter(id=self.alice.id).exists())
        self.assertEqual(post.comments_count, 0)

        # 5. Comment & Atomic Counter Rollup
        self.client.force_authenticate(user=self.bob)
        res_comment = self.client.post("/api/populate/create/feed_comment/", {
            "post": post_id,
            "content": "Excited for this kickoff!"
        }, format="json")
        self.assertEqual(res_comment.status_code, 201)
        post.refresh_from_db()
        self.assertEqual(post.comments_count, 1)
        self.assertTrue(post.followers.filter(id=self.bob.id).exists())

        # 6. Direct Message Anti-Spoofing
        res_msg_spoof = self.client.post("/api/populate/create/team_message/", {
            "sender": self.alice.id,
            "recipient": self.charlie.id,
            "message": "Impersonated message"
        }, format="json")
        self.assertIn(res_msg_spoof.status_code, (400, 403))

        # 7. Self-Messaging Prevention
        res_msg_self = self.client.post("/api/populate/create/team_message/", {
            "recipient": self.bob.id,
            "message": "Self ping"
        }, format="json")
        self.assertIn(res_msg_self.status_code, (400, 403, 500))

        # 8. Legitimate DM & Deterministic Conversation ID
        res_dm = self.client.post("/api/populate/create/team_message/", {
            "recipient": self.alice.id,
            "message": "Hey Alice, do you have a minute to review PR #42?"
        }, format="json")
        self.assertEqual(res_dm.status_code, 201)
        dm_item = res_dm.data["data"]
        msg_id = dm_item[0]["id"] if isinstance(dm_item, list) else dm_item["id"]
        msg = TeamMessage.objects.get(id=msg_id)
        self.assertEqual(msg.sender_id, self.bob.id)
        self.assertEqual(msg.recipient_id, self.alice.id)
        sorted_ids = sorted([str(self.bob.id), str(self.alice.id)])
        self.assertEqual(msg.conversation_id, f"{sorted_ids[0]}_{sorted_ids[1]}")
        self.assertEqual(msg.status, "sent")
        self.assertIsNone(msg.delivered_at)
        self.assertIsNone(msg.read_at)

        # 9. Sender cannot mark sent message as read
        res_bad_read = self.client.post(f"/api/populate/update/team_message/{msg_id}/", {
            "status": "read"
        }, format="json")
        self.assertIn(res_bad_read.status_code, (400, 403))

        # 10. Recipient Alice marks delivered and read
        self.client.force_authenticate(user=self.alice)
        res_delivered = self.client.post(f"/api/populate/update/team_message/{msg_id}/", {
            "status": "delivered"
        }, format="json")
        self.assertEqual(res_delivered.status_code, 200)
        msg.refresh_from_db()
        self.assertEqual(msg.status, "delivered")
        self.assertIsNotNone(msg.delivered_at)

        res_read = self.client.post(f"/api/populate/update/team_message/{msg_id}/", {
            "status": "read"
        }, format="json")
        self.assertEqual(res_read.status_code, 200)
        msg.refresh_from_db()
        self.assertEqual(msg.status, "read")
        self.assertIsNotNone(msg.read_at)

        # 11. Invalid backward transition
        res_backward = self.client.post(f"/api/populate/update/team_message/{msg_id}/", {
            "status": "sent"
        }, format="json")
        self.assertIn(res_backward.status_code, (400, 403, 500))

        # 12. DM Privacy: Charlie cannot see Bob <-> Alice messages
        self.client.force_authenticate(user=self.charlie)
        res_charlie_read = self.client.post("/api/populate/read/team_message/", {}, format="json")
        charlie_msg_ids = [m["id"] for m in res_charlie_read.data.get("data", [])]
        self.assertNotIn(msg_id, charlie_msg_ids)

        # Alice sees it in her inbox
        self.client.force_authenticate(user=self.alice)
        res_alice_read = self.client.post("/api/populate/read/team_message/", {}, format="json")
        alice_msg_ids = [m["id"] for m in res_alice_read.data.get("data", [])]
        self.assertIn(msg_id, alice_msg_ids)
