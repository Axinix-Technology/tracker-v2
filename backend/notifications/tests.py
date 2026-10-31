from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from notifications.models import Notification
from users.models import Role

User = get_user_model()


class NotificationSecurityTestCase(TestCase):
    def setUp(self):
        self.role_emp, _ = Role.objects.get_or_create(
            name="Employee", defaults={"is_superadmin": False, "status": 1}
        )

        self.alice = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="AlicePassword123!",
            role=self.role_emp
        )

        self.bob = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="BobPassword123!",
            role=self.role_emp
        )

        self.client = APIClient()

        # Seed notifications for Alice and Bob
        self.notif_alice = Notification.objects.create(
            recipient=self.alice,
            sender=self.bob,
            title="Hello Alice",
            message="Message for Alice only",
            is_read=False
        )

        self.notif_bob = Notification.objects.create(
            recipient=self.bob,
            sender=self.alice,
            title="Hello Bob",
            message="Message for Bob only",
            is_read=False
        )

    def test_recipient_isolation_on_read(self):
        self.client.force_authenticate(user=self.alice)
        res = self.client.post("/api/populate/read/notification/", {}, format="json")
        self.assertEqual(res.status_code, 200)
        items = res.data["data"]
        ids = [item["id"] for item in items]

        # Alice must see her notification and MUST NOT see Bob's notification
        self.assertIn(self.notif_alice.id, ids)
        self.assertNotIn(self.notif_bob.id, ids)

    def test_sender_spoofing_prevented_on_create(self):
        self.client.force_authenticate(user=self.alice)
        res = self.client.post(
            "/api/populate/create/notification/",
            {
                "recipient": self.bob.id,
                "sender": self.bob.id,  # Alice attempts to spoof sender as Bob
                "title": "Spoofed Notification",
                "message": "I am pretending to be Bob sending a message to Bob",
            },
            format="json"
        )
        self.assertEqual(res.status_code, 201)
        created_data = res.data["data"]
        notif_id = created_data[0]["id"] if isinstance(created_data, list) else created_data["id"]

        notif = Notification.objects.get(id=notif_id)
        # Sender must strictly be Alice, not the spoofed Bob
        self.assertEqual(notif.sender.id, self.alice.id)

    def test_cannot_update_another_users_notification(self):
        self.client.force_authenticate(user=self.alice)
        res = self.client.post(
            f"/api/populate/update/notification/{self.notif_bob.id}/",
            {"isRead": True},
            format="json"
        )
        # Scoped queryset returns 404 (does not exist in user's scope) or 403 Forbidden
        self.assertIn(res.status_code, (400, 403, 404))
        self.notif_bob.refresh_from_db()
        self.assertFalse(self.notif_bob.is_read)

    def test_can_update_own_notification(self):
        self.client.force_authenticate(user=self.alice)
        res = self.client.post(
            f"/api/populate/update/notification/{self.notif_alice.id}/",
            {"isRead": True},
            format="json"
        )
        self.assertEqual(res.status_code, 200)
        self.notif_alice.refresh_from_db()
        self.assertTrue(self.notif_alice.is_read)
