from django.db import models
from django.conf import settings
from populate_core.registry import register_model

@register_model("notification", table_type="transaction", aliases=["notifications"])
class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications"
    )
    type = models.CharField(max_length=64, default="system")
    title = models.CharField(max_length=255)
    message = models.TextField()
    path = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"

    def __str__(self):
        return self.title

    @property
    def isRead(self):
        return self.is_read


@register_model("notification_receptionist", table_type="transaction", aliases=["notification_receptionists", "notificationreceptionist"])
class NotificationReceptionist(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="receptionists")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_notifications")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notification_receptionists"

    def __str__(self):
        return f"{self.receiver} - {self.notification_id}"


@register_model("notification_rule", table_type="master", aliases=["notification_rules", "notificationrules", "notificationrule"])
class NotificationRule(models.Model):
    company = models.CharField(max_length=128, default="Work Hub ERP")
    name = models.CharField(max_length=255)
    model_name = models.CharField(max_length=128, db_index=True)  # e.g. "tasks", "tickets"
    trigger = models.CharField(
        max_length=64,
        db_index=True,
        help_text="create, update, delete, approve, reject, transition, custom"
    )
    enabled = models.BooleanField(default=True, db_index=True)
    priority = models.IntegerField(default=0, db_index=True)
    stop_processing = models.BooleanField(default=False)

    condition_groups = models.JSONField(
        default=dict,
        help_text="operator (AND/OR) and conditions array"
    )
    recipients = models.JSONField(
        default=dict,
        help_text="fields, roles, customResolvers, queries"
    )
    template = models.JSONField(
        default=dict,
        help_text="title, message, type, path, icon, priority, category"
    )

    version = models.IntegerField(default=1)
    published_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_notification_rules"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_notification_rules"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_rules"

    def __str__(self):
        return self.name


@register_model("notification_preference", table_type="master", aliases=["notification_preferences", "notificationpreference", "notificationpreferences"])
class NotificationPreference(models.Model):
    employee = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        db_index=True
    )
    mute_task_status_changes = models.BooleanField(default=False)
    mute_task_assignments = models.BooleanField(default=False)
    mute_task_comments = models.BooleanField(default=False)
    only_mentions = models.BooleanField(default=False)
    daily_digest_only = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_preferences"

    def __str__(self):
        return f"Prefs for {self.employee_id}"
