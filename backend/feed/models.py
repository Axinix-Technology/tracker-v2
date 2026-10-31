from django.db import models
from django.conf import settings
from django.utils import timezone
from populate_core.registry import register_model


# ============================================================================
# 1. FEED GROUP
# ============================================================================

@register_model("feed_group", table_type="master", aliases=["feed_groups"])
class FeedGroup(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="feed_groups")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_feed_groups"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "feed_groups"
        indexes = [
            models.Index(fields=["status", "name"]),
        ]

    def __str__(self):
        return self.name


# ============================================================================
# 2. FEED CHANNEL
# ============================================================================

@register_model("feed_channel", table_type="master", aliases=["feed_channels"])
class FeedChannel(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    description = models.TextField(blank=True, null=True)
    groups = models.ManyToManyField(FeedGroup, blank=True, related_name="channels")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="feed_channels")
    is_external = models.BooleanField(default=False)
    allowed_clients = models.ManyToManyField("users.Client", blank=True, related_name="feed_channels")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_feed_channels"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "feed_channels"
        indexes = [
            models.Index(fields=["status", "name"]),
        ]

    def __str__(self):
        return self.name


# ============================================================================
# 3. FEED POST
# ============================================================================

@register_model("feed_post", table_type="transaction", aliases=["feed_posts"])
class FeedPost(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="feed_posts"
    )
    post_type = models.CharField(max_length=32, default="General", db_index=True)  # Update, Announcement, Question, General, Poll
    subject = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    attachments = models.JSONField(default=list)
    
    group = models.ForeignKey(
        FeedGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts"
    )
    channel = models.ForeignKey(
        FeedChannel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts"
    )
    channels = models.ManyToManyField(FeedChannel, blank=True, related_name="multi_channel_posts")
    is_broadcast = models.BooleanField(default=False, db_index=True)
    
    poll_options = models.JSONField(default=list)  # [{ "optionText": str, "votes": [int] }]
    mentions = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="mentioned_in_posts")
    reactions = models.JSONField(default=list)  # [{ "user_id": int, "reaction_type": str, "created_at": iso }]
    
    comments_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    viewed_by = models.JSONField(default=list)  # [{ "user_id": int, "viewed_at": iso }]
    
    pinned_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="pinned_posts")
    bookmarked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="bookmarked_posts")
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="followed_posts")
    
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False, db_index=True)
    is_draft = models.BooleanField(default=False, db_index=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "feed_posts"
        indexes = [
            models.Index(fields=["status", "post_type", "created_at"]),
            models.Index(fields=["status", "channel", "created_at"]),
            models.Index(fields=["status", "group", "created_at"]),
            models.Index(fields=["status", "is_broadcast", "created_at"]),
        ]

    def __str__(self):
        prefix = f"[{self.post_type}] " if self.post_type else ""
        title = self.subject or self.content[:40]
        return f"{prefix}{title}"


# ============================================================================
# 4. FEED COMMENT
# ============================================================================

@register_model("feed_comment", table_type="transaction", aliases=["feed_comments"])
class FeedComment(models.Model):
    post = models.ForeignKey(
        FeedPost,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="feed_comments"
    )
    content = models.TextField()
    attachments = models.JSONField(default=list)
    mentions = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="mentioned_in_comments")
    reactions = models.JSONField(default=list)
    replies = models.JSONField(default=list)  # [{ "author_id": int, "content": str, "mentions": [], "created_at": iso }]
    
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "feed_comments"
        indexes = [
            models.Index(fields=["status", "post", "created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.author} on {self.post_id}"


# ============================================================================
# 5. TEAM MESSAGE (DIRECT 1-ON-1 & CHAT)
# ============================================================================

@register_model("team_message", table_type="transaction", aliases=["team_messages"])
class TeamMessage(models.Model):
    conversation_id = models.CharField(max_length=128, db_index=True, blank=True)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_team_messages"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_team_messages"
    )
    message = models.TextField(blank=True, default="")
    message_type = models.CharField(max_length=32, default="text", db_index=True)  # text, image, file, voice, system
    attachments = models.JSONField(default=list)
    status = models.CharField(max_length=32, default="sent", db_index=True)  # sent, delivered, read
    sent_at = models.DateTimeField(default=timezone.now, db_index=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    reactions = models.JSONField(default=list)
    reply_to = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies"
    )
    is_deleted = models.BooleanField(default=False, db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "team_messages"
        indexes = [
            models.Index(fields=["lifecycle_status", "conversation_id", "sent_at"]),
            models.Index(fields=["lifecycle_status", "recipient", "status"]),
            models.Index(fields=["lifecycle_status", "sender", "recipient"]),
        ]

    def __str__(self):
        return f"Msg {self.sender} -> {self.recipient}: {self.message[:30]}"
