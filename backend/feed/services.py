import logging
from django.db import models, transaction
from django.utils import timezone
from populate_core.registry import BaseService, register_service
from populate_core.response.exceptions import AuthorizationError, ValidationError, NotFoundError

logger = logging.getLogger("feed.services")


# ============================================================================
# 1. FEED POST SERVICE
# ============================================================================

@register_service("feed_post")
class FeedPostService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        user = getattr(context, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return models.Q(pk__isnull=True)
        if getattr(user, "is_superadmin", False):
            return None

        # Row-level visibility: broadcast, public feed, channel member, internal channel, group member, or own post
        return (
            models.Q(is_broadcast=True)
            | models.Q(channel__isnull=True, group__isnull=True)
            | models.Q(channel__is_external=False)
            | models.Q(channel__members=user)
            | models.Q(group__members=user)
            | models.Q(author=user)
        )

    def before_read(self, context, queryset):
        queryset = super().before_read(context, queryset)
        user = getattr(context, "user", None)
        if not getattr(user, "is_superadmin", False):
            queryset = queryset.filter(is_deleted=False)
            scope = self.get_policy_scope(context)
            if scope:
                queryset = queryset.filter(scope).distinct()
        return queryset

    def before_create(self, context, data):
        user = getattr(context, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            raise AuthorizationError("Authentication required to create a feed post.")

        if not data.get("content"):
            raise ValueError("Post content is required.")

        # Sender identity: always derive from authenticated user
        author_id = user.id
        req_author = data.get("author") or data.get("author_id")
        if req_author and str(req_author) != str(author_id) and not getattr(user, "is_superadmin", False):
            raise AuthorizationError("Cannot author a post on behalf of another user.")
        data["author_id"] = author_id

        # Verify target channel authorization
        channel_id = data.get("channel") or data.get("channel_id")
        if channel_id:
            from .models import FeedChannel
            try:
                channel = FeedChannel.objects.get(id=channel_id, status=1)
                if channel.is_external:
                    is_member = channel.members.filter(id=user.id).exists()
                    has_client_access = False
                    if hasattr(user, "client") and user.client:
                        has_client_access = channel.allowed_clients.filter(id=user.client.id).exists()
                    if not is_member and not has_client_access and not getattr(user, "is_superadmin", False):
                        raise AuthorizationError(f"You do not have access to post in external channel #{channel.name}.")
            except FeedChannel.DoesNotExist:
                raise NotFoundError(f"Channel with ID {channel_id} not found.")

        # Verify target group authorization
        group_id = data.get("group") or data.get("group_id")
        if group_id:
            from .models import FeedGroup
            try:
                group = FeedGroup.objects.get(id=group_id, status=1)
                if not group.members.filter(id=user.id).exists() and not getattr(user, "is_superadmin", False):
                    raise AuthorizationError(f"You must be a member of group '{group.name}' to post.")
            except FeedGroup.DoesNotExist:
                raise NotFoundError(f"Group with ID {group_id} not found.")

        data["comments_count"] = 0
        data["views_count"] = 0
        data["reactions"] = data.get("reactions", [])
        data["viewed_by"] = []
        data["post_type"] = data.get("post_type", "General")
        data["status"] = data.get("status", 1)

        return data

    def before_update(self, context, instance, data):
        user = getattr(context, "user", None)
        is_admin = getattr(user, "is_superadmin", False)

        # Protect immutable identity fields
        data.pop("author", None)
        data.pop("author_id", None)
        data.pop("created_at", None)

        # If mutating content, subject, attachments, or channel/group: must be author or superadmin
        content_fields = {"content", "subject", "attachments", "group", "channel", "is_broadcast", "poll_options"}
        if any(f in data for f in content_fields):
            if instance.author_id != user.id and not is_admin:
                raise AuthorizationError("Only the author or an administrator can edit post content.")
            data["is_edited"] = True

        # Concurrency safety for reactions: allow user to toggle their own reaction cleanly
        if "reaction" in data and isinstance(data["reaction"], dict):
            reaction_type = data["reaction"].get("reaction_type")
            current_reactions = list(instance.reactions)
            # Remove existing reaction from this user if any
            updated_reactions = [r for r in current_reactions if r.get("user_id") != user.id]
            if reaction_type:
                updated_reactions.append({
                    "user_id": user.id,
                    "reaction_type": reaction_type,
                    "created_at": timezone.now().isoformat()
                })
            data["reactions"] = updated_reactions
            data.pop("reaction", None)

        # Record view cleanly without clobbering
        if data.get("record_view"):
            current_views = list(instance.viewed_by)
            if not any(v.get("user_id") == user.id for v in current_views):
                current_views.append({
                    "user_id": user.id,
                    "viewed_at": timezone.now().isoformat()
                })
                data["viewed_by"] = current_views
                data["views_count"] = len(current_views)
            data.pop("record_view", None)

        return data

    def before_delete(self, context, instance):
        user = getattr(context, "user", None)
        if instance.author_id != user.id and not getattr(user, "is_superadmin", False):
            raise AuthorizationError("Only the author or an administrator can delete this post.")

    def after_create(self, context, instance):
        # 1. Author automatically follows their own post
        if instance.author:
            instance.followers.add(instance.author)

        # 2. Side effects via transaction.on_commit with recipient union & structured error handling
        def on_commit_feed_post():
            try:
                from notifications.models import Notification
                author = instance.author
                author_id = instance.author_id

                recipient_ids = set()

                # A. Broadcast announcement -> all active users
                if instance.is_broadcast:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    all_ids = User.objects.filter(is_active=True).values_list("id", flat=True)
                    recipient_ids.update(all_ids)

                # B. Primary channel members
                if instance.channel_id:
                    recipient_ids.update(instance.channel.members.values_list("id", flat=True))

                # C. Additional multi-channels
                if instance.channels.exists():
                    recipient_ids.update(instance.channels.values_list("members__id", flat=True))

                # D. Group members
                if instance.group_id:
                    recipient_ids.update(instance.group.members.values_list("id", flat=True))

                # E. Mentioned users
                if instance.mentions.exists():
                    recipient_ids.update(instance.mentions.values_list("id", flat=True))

                # Exclude author & None
                recipient_ids.discard(author_id)
                recipient_ids.discard(None)

                if not recipient_ids:
                    return

                notifications = [
                    Notification(
                        recipient_id=uid,
                        sender_id=author_id,
                        type="feed_post",
                        title=f"New Post: {instance.subject or 'Team Feed'}",
                        message=f"{author.username if author else 'User'}: {instance.content[:80]}...",
                        path=f"/feed/{instance.id}"
                    )
                    for uid in recipient_ids
                ]

                Notification.objects.bulk_create(notifications, ignore_conflicts=True)
                logger.info(f"[FeedPost] Dispatched {len(notifications)} notifications for post #{instance.id}.")

            except Exception as e:
                logger.error(f"[FeedPost Notification Error] Failed to create notifications for post #{instance.id}: {e}", exc_info=True)

        transaction.on_commit(on_commit_feed_post)
        return instance


# ============================================================================
# 2. FEED COMMENT SERVICE
# ============================================================================

@register_service("feed_comment")
class FeedCommentService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def before_read(self, context, queryset):
        queryset = super().before_read(context, queryset)
        return queryset.filter(status=1)

    def before_create(self, context, data):
        user = getattr(context, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            raise AuthorizationError("Authentication required to comment.")

        if not data.get("content"):
            raise ValueError("Comment content cannot be empty.")
        if not data.get("post") and not data.get("post_id"):
            raise ValueError("post is required for FeedComment.")

        # Sender identity: always derive from authenticated user
        author_id = user.id
        req_author = data.get("author") or data.get("author_id")
        if req_author and str(req_author) != str(author_id) and not getattr(user, "is_superadmin", False):
            raise AuthorizationError("Cannot comment on behalf of another user.")
        data["author_id"] = author_id

        # Verify parent post exists and is active
        from .models import FeedPost
        post_id = data.get("post") or data.get("post_id")
        try:
            post = FeedPost.objects.get(id=post_id, is_deleted=False)
            data["post_id"] = post.id
        except FeedPost.DoesNotExist:
            raise NotFoundError(f"Post with ID {post_id} not found or deleted.")

        return data

    def before_update(self, context, instance, data):
        user = getattr(context, "user", None)
        is_admin = getattr(user, "is_superadmin", False)

        # Protect immutable fields
        data.pop("author", None)
        data.pop("author_id", None)
        data.pop("post", None)
        data.pop("post_id", None)
        data.pop("created_at", None)

        if "content" in data and data["content"] != instance.content:
            if instance.author_id != user.id and not is_admin:
                raise AuthorizationError("Only the comment author or an administrator can edit this comment.")

        return data

    def before_delete(self, context, instance):
        user = getattr(context, "user", None)
        is_admin = getattr(user, "is_superadmin", False)
        # Author of comment OR author of post OR superadmin can delete comment
        if instance.author_id != user.id and instance.post.author_id != user.id and not is_admin:
            raise AuthorizationError("Only the comment author, post author, or an administrator can delete this comment.")

    def after_create(self, context, instance):
        from .models import FeedPost

        # 1. Atomically increment comments_count on parent post
        FeedPost.objects.filter(id=instance.post_id).update(
            comments_count=models.F("comments_count") + 1
        )

        # 2. Commenter automatically follows the post
        if instance.author:
            instance.post.followers.add(instance.author)

        # 3. Side effects on_commit (notify post author, followers, and mentioned users)
        def on_commit_comment():
            try:
                from notifications.models import Notification
                author = instance.author
                author_id = instance.author_id
                post = instance.post

                recipient_ids = set()

                # A. Post author
                if post.author_id:
                    recipient_ids.add(post.author_id)

                # B. Post followers
                follower_ids = post.followers.values_list("id", flat=True)
                recipient_ids.update(follower_ids)

                # C. Mentioned users in comment
                if instance.mentions.exists():
                    recipient_ids.update(instance.mentions.values_list("id", flat=True))

                # Exclude comment author and None
                recipient_ids.discard(author_id)
                recipient_ids.discard(None)

                if not recipient_ids:
                    return

                notifications = [
                    Notification(
                        recipient_id=uid,
                        sender_id=author_id,
                        type="feed_comment",
                        title=f"New comment on post: {post.subject or 'Team Feed'}",
                        message=f"{author.username if author else 'User'}: {instance.content[:80]}...",
                        path=f"/feed/{post.id}"
                    )
                    for uid in recipient_ids
                ]

                Notification.objects.bulk_create(notifications, ignore_conflicts=True)
                logger.info(f"[FeedComment] Dispatched {len(notifications)} notifications for comment #{instance.id}.")

            except Exception as e:
                logger.error(f"[FeedComment Notification Error] Failed to create notifications for comment #{instance.id}: {e}", exc_info=True)

        transaction.on_commit(on_commit_comment)
        return instance


# ============================================================================
# 3. TEAM MESSAGE SERVICE (1-ON-1 DIRECT CHAT)
# ============================================================================

@register_service("team_message")
class TeamMessageService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        user = getattr(context, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return models.Q(pk__isnull=True)
        if getattr(user, "is_superadmin", False):
            return None
        # Strict privacy: only sender or recipient can see the direct message
        return models.Q(sender=user) | models.Q(recipient=user)

    def before_read(self, context, queryset):
        queryset = super().before_read(context, queryset)
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return queryset
        if not user or not getattr(user, "is_authenticated", False):
            return queryset.none()
        # Direct messages are strictly private between sender and recipient
        return queryset.filter(models.Q(sender=user) | models.Q(recipient=user)).filter(is_deleted=False)

    def before_create(self, context, data):
        user = getattr(context, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            raise AuthorizationError("Authentication required to send a team message.")

        if not data.get("message") and not data.get("attachments"):
            raise ValueError("Message content or attachment is required.")

        # Sender identity: strictly derive from authenticated user
        sender_id = user.id
        req_sender = data.get("sender") or data.get("sender_id")
        if req_sender and str(req_sender) != str(sender_id) and not getattr(user, "is_superadmin", False):
            raise AuthorizationError("Cannot send a direct message on behalf of another user.")
        data["sender_id"] = sender_id

        recipient_id = data.get("recipient") or data.get("recipient_id")
        if not recipient_id:
            raise ValueError("recipient is required.")

        if str(sender_id) == str(recipient_id):
            raise ValueError("Cannot send a direct message to yourself.")
        data["recipient_id"] = recipient_id

        # Deterministic string sorting handles both integer IDs and UUID strings
        sorted_ids = sorted([str(sender_id), str(recipient_id)])
        data["conversation_id"] = f"{sorted_ids[0]}_{sorted_ids[1]}"

        # Server-enforced initial state
        data["status"] = "sent"
        data["sent_at"] = timezone.now()
        data.pop("delivered_at", None)
        data.pop("read_at", None)

        return data

    def before_update(self, context, instance, data):
        user = getattr(context, "user", None)
        is_admin = getattr(user, "is_superadmin", False)

        # Protect immutable identity & timestamp fields
        for immutable in ("sender", "sender_id", "recipient", "recipient_id", "conversation_id", "sent_at"):
            data.pop(immutable, None)

        # Prevent clients from providing arbitrary timestamps
        data.pop("delivered_at", None)
        data.pop("read_at", None)

        new_status = data.get("status")
        now = timezone.now()

        # Status transition validation
        if new_status:
            # Only recipient (or superadmin) can update delivery / read status
            if user.id != instance.recipient_id and not is_admin:
                raise AuthorizationError("Only the message recipient can update message status.")

            valid_transitions = {
                "sent": ["delivered", "read"],
                "delivered": ["read"],
                "read": [],  # Terminal state
            }
            current_status = instance.status
            if new_status != current_status:
                allowed = valid_transitions.get(current_status, [])
                if new_status not in allowed:
                    raise ValueError(f"Invalid message status transition from '{current_status}' to '{new_status}'.")

                if new_status == "delivered":
                    data["delivered_at"] = instance.delivered_at or now
                elif new_status == "read":
                    data["delivered_at"] = instance.delivered_at or now
                    data["read_at"] = instance.read_at or now

        # Message content editing: only sender (within edit window) or superadmin
        if "message" in data and data["message"] != instance.message:
            if user.id != instance.sender_id and not is_admin:
                raise AuthorizationError("Only the author can edit message content.")

        return data

    def before_delete(self, context, instance):
        user = getattr(context, "user", None)
        is_admin = getattr(user, "is_superadmin", False)
        # Only sender or superadmin can delete a message
        if user.id != instance.sender_id and not is_admin:
            raise AuthorizationError("Only the sender or an administrator can delete this message.")

    def after_create(self, context, instance):
        def on_commit_message():
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=instance.recipient,
                    sender=instance.sender,
                    type="direct_message",
                    title=f"Message from {instance.sender.username}",
                    message=f"{instance.message[:80]}...",
                    path=f"/messages/{instance.conversation_id}"
                )
                logger.info(f"[TeamMessage] Dispatched direct message notification #{instance.id} from {instance.sender.username} to {instance.recipient.username}.")
            except Exception as e:
                logger.error(f"[TeamMessage Notification Error] Failed to create notification for message #{instance.id}: {e}", exc_info=True)

        transaction.on_commit(on_commit_message)
        return instance


# ============================================================================
# 4. FEED CHANNEL & FEED GROUP SERVICES
# ============================================================================

@register_service("feed_channel")
class FeedChannelService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        user = getattr(context, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return models.Q(pk__isnull=True)
        if getattr(user, "is_superadmin", False):
            return None
        # Internal channels visible to all staff; external channels only to members and allowed clients
        client_q = models.Q(allowed_clients=user.client) if (hasattr(user, "client") and user.client) else models.Q(pk__isnull=True)
        return models.Q(is_external=False) | models.Q(members=user) | client_q

    def before_read(self, context, queryset):
        queryset = super().before_read(context, queryset)
        user = getattr(context, "user", None)
        if not getattr(user, "is_superadmin", False):
            queryset = queryset.filter(status=1)
            scope = self.get_policy_scope(context)
            if scope:
                queryset = queryset.filter(scope).distinct()
        return queryset

    def before_create(self, context, data):
        user = getattr(context, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            raise AuthorizationError("Authentication required to create a channel.")

        if not data.get("name"):
            raise ValueError("Channel name is required.")

        data["created_by_id"] = user.id
        data["status"] = data.get("status", 1)
        return data

    def before_update(self, context, instance, data):
        user = getattr(context, "user", None)
        is_admin = getattr(user, "is_superadmin", False)
        # Protect creator
        data.pop("created_by", None)
        data.pop("created_by_id", None)
        if instance.created_by_id != user.id and not is_admin:
            raise AuthorizationError("Only the channel creator or an administrator can modify this channel.")
        return data

    def before_delete(self, context, instance):
        user = getattr(context, "user", None)
        if instance.created_by_id != user.id and not getattr(user, "is_superadmin", False):
            raise AuthorizationError("Only the channel creator or an administrator can delete this channel.")

    def after_create(self, context, instance):
        if instance.created_by:
            instance.members.add(instance.created_by)
        return instance


@register_service("feed_group")
class FeedGroupService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        user = getattr(context, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return models.Q(pk__isnull=True)
        if getattr(user, "is_superadmin", False):
            return None
        return models.Q(members=user) | models.Q(created_by=user)

    def before_read(self, context, queryset):
        queryset = super().before_read(context, queryset)
        user = getattr(context, "user", None)
        if not getattr(user, "is_superadmin", False):
            queryset = queryset.filter(status=1)
            scope = self.get_policy_scope(context)
            if scope:
                queryset = queryset.filter(scope).distinct()
        return queryset

    def before_create(self, context, data):
        user = getattr(context, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            raise AuthorizationError("Authentication required to create a group.")

        if not data.get("name"):
            raise ValueError("Group name is required.")

        data["created_by_id"] = user.id
        data["status"] = data.get("status", 1)
        return data

    def before_update(self, context, instance, data):
        user = getattr(context, "user", None)
        is_admin = getattr(user, "is_superadmin", False)
        data.pop("created_by", None)
        data.pop("created_by_id", None)
        if instance.created_by_id != user.id and not is_admin:
            raise AuthorizationError("Only the group creator or an administrator can modify this group.")
        return data

    def before_delete(self, context, instance):
        user = getattr(context, "user", None)
        if instance.created_by_id != user.id and not getattr(user, "is_superadmin", False):
            raise AuthorizationError("Only the group creator or an administrator can delete this group.")

    def after_create(self, context, instance):
        if instance.created_by:
            instance.members.add(instance.created_by)
        return instance
