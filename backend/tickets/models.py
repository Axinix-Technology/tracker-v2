from django.db import models
from django.conf import settings
from populate_core.registry import register_model


# ============================================================================
# 1. TICKET MASTER
# ============================================================================

@register_model("ticket", table_type="transaction", aliases=["tickets"])
class Ticket(models.Model):
    ticket_id = models.CharField(max_length=64, unique=True, blank=True, null=True, db_index=True)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    user_story = models.TextField(blank=True, null=True)
    client = models.ForeignKey("users.Client", on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets")
    project_type = models.ForeignKey("users.ProjectType", on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets")
    priority = models.CharField(max_length=32, default="Medium", db_index=True)
    ticket_status = models.CharField(max_length=64, default="Open", db_index=True)
    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_tickets")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    linked_task = models.ForeignKey("tasks.Task", on_delete=models.SET_NULL, null=True, blank=True, related_name="linked_tickets")
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tickets"
        indexes = [
            models.Index(fields=["status", "ticket_status", "client"]),
            models.Index(fields=["status", "assignee", "priority"]),
            models.Index(fields=["status", "meta_status", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.ticket_id or self.id}] {self.title}"


# ============================================================================
# 2. TICKET COMMENTS
# ============================================================================

@register_model("ticket_comment", table_type="transaction", aliases=["ticket_comments"])
class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ticket_comments")
    content = models.TextField()
    is_internal = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ticket_comments"
        indexes = [
            models.Index(fields=["status", "ticket", "created_at"]),
        ]

    def __str__(self):
        return f"Comment on {self.ticket_id}"


# ============================================================================
# 3. TICKET ATTACHMENTS
# ============================================================================

@register_model("ticket_attachment", table_type="transaction", aliases=["ticket_attachments"])
class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="attachments")
    file_url = models.CharField(max_length=512)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ticket_attachments")
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ticket_attachments"
        indexes = [
            models.Index(fields=["status", "ticket"]),
        ]

    def __str__(self):
        return self.file_name


# ============================================================================
# 4. TICKET ACTIVITY LOGS
# ============================================================================

@register_model("ticket_activity_log", table_type="transaction", aliases=["ticket_activity_logs"])
class TicketActivityLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="activity_logs")
    action = models.CharField(max_length=64, db_index=True)  # created, assigned, status_changed, comment_added, attachment_uploaded
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ticket_activities")
    details = models.JSONField(default=dict)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ticket_activity_logs"
        indexes = [
            models.Index(fields=["status", "ticket", "created_at"]),
            models.Index(fields=["status", "action"]),
        ]

    def __str__(self):
        return f"{self.action} on {self.ticket_id}"


# ============================================================================
# 5. TICKET PARTICIPANTS
# ============================================================================

@register_model("ticket_participant", table_type="transaction", aliases=["ticket_participants"])
class TicketParticipant(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ticket_participations")
    role = models.CharField(max_length=32, default="watcher")  # creator, assignee, watcher, manager
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ticket_participants"
        constraints = [
            models.UniqueConstraint(fields=["ticket", "user"], name="uniq_ticket_user_participant")
        ]
        indexes = [
            models.Index(fields=["status", "ticket", "role"]),
            models.Index(fields=["status", "user"]),
        ]

    def __str__(self):
        return f"{self.user} as {self.role} on {self.ticket_id}"


# ============================================================================
# 6. TICKET STATUS HISTORY
# ============================================================================

@register_model("ticket_status_history", table_type="transaction", aliases=["ticket_status_history"])
class TicketStatusHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=64, blank=True, null=True)
    to_status = models.CharField(max_length=64, db_index=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ticket_status_changes")
    duration_seconds = models.PositiveIntegerField(default=0)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ticket_status_history"
        indexes = [
            models.Index(fields=["status", "ticket", "created_at"]),
        ]

    def __str__(self):
        return f"Status {self.from_status} -> {self.to_status} on {self.ticket_id}"
