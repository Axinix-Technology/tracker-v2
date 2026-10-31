import datetime
import logging
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from populate_core.registry import BaseService, register_service

logger = logging.getLogger(__name__)


# ============================================================================
# 1. TICKET SERVICE
# ============================================================================

@register_service("ticket")
class TicketService(BaseService):
    def check_permission(self, context):
        if getattr(context.user, "is_superadmin", False):
            return True
        if getattr(context.user, "is_authenticated", False):
            return True
        return None

    def get_policy_scope(self, context):
        if getattr(context.user, "is_superadmin", False):
            return Q()
        return Q(meta_status="active", status=1)

    def before_create(self, context, data):
        if not data.get("title"):
            raise ValueError("Ticket title is required.")

        from .models import Ticket

        # 1. Sequential ticket_id generation (TCK-1, TCK-2, ...)
        if not data.get("ticket_id"):
            last_ticket = Ticket.objects.order_by("-id").first()
            next_num = (last_ticket.id + 1) if last_ticket else 1
            generated_key = f"TCK-{next_num}"
            while Ticket.objects.filter(ticket_id=generated_key).exists():
                next_num += 1
                generated_key = f"TCK-{next_num}"
            data["ticket_id"] = generated_key

        # 2. Defaults
        data["ticket_status"] = data.get("ticket_status", "Open")
        data["priority"] = data.get("priority", "Medium")
        data["meta_status"] = data.get("meta_status", "active")
        data["status"] = data.get("status", 1)

        # 3. Creator: strictly derive from authenticated user to prevent identity spoofing
        if hasattr(context, "user") and getattr(context.user, "is_authenticated", False):
            if not getattr(context.user, "is_superadmin", False):
                data["created_by_id"] = context.user.id
            elif not data.get("created_by") and not data.get("created_by_id"):
                data["created_by_id"] = context.user.id

        return data

    def after_create(self, context, instance):
        from .models import TicketParticipant, TicketActivityLog, TicketStatusHistory

        # 1. Register creator participant
        if instance.created_by:
            TicketParticipant.objects.get_or_create(
                ticket=instance,
                user=instance.created_by,
                defaults={"role": "creator"}
            )

        # 2. Register assignee participant
        if instance.assignee and instance.assignee != instance.created_by:
            TicketParticipant.objects.get_or_create(
                ticket=instance,
                user=instance.assignee,
                defaults={"role": "assignee"}
            )

        # 3. Record initial activity log
        TicketActivityLog.objects.create(
            ticket=instance,
            action="created",
            performed_by=instance.created_by,
            details={"priority": instance.priority, "status": instance.ticket_status}
        )

        # 4. Record initial status history
        TicketStatusHistory.objects.create(
            ticket=instance,
            from_status=None,
            to_status=instance.ticket_status,
            changed_by=instance.created_by,
            duration_seconds=0
        )

        # 5. Side effects on_commit (notifications & task link back)
        def on_commit_ticket_create():
            try:
                from notifications.models import Notification
                # Notify assignee
                if instance.assignee and instance.assignee != instance.created_by:
                    Notification.objects.create(
                        recipient=instance.assignee,
                        sender=instance.created_by,
                        type="ticket_assignment",
                        title=f"New Ticket Assigned: {instance.ticket_id}",
                        message=f"You have been assigned to ticket '{instance.title}'",
                        path=f"/tickets/{instance.id}"
                    )

                # Link back to Task if linked_task was set
                if instance.linked_task:
                    task = instance.linked_task
                    if not task.linkedTicketId:
                        task.linkedTicketId = instance
                        task.isFromTicket = True
                        task.save(update_fields=["linkedTicketId", "isFromTicket"])
            except Exception:
                logger.exception("Error in on_commit_ticket_create side effects")

        transaction.on_commit(on_commit_ticket_create)
        return instance

    def before_update(self, context, instance, data):
        # 1. Capture previous status for transition tracking
        instance._pre_update_status = instance.ticket_status
        context.metadata["prev_ticket_status"] = instance.ticket_status

        # 2. Transition timestamping
        new_status = data.get("ticket_status")
        if new_status and new_status != instance.ticket_status:
            now = timezone.now()
            if new_status == "Resolved" and not instance.resolved_at:
                data["resolved_at"] = now
            elif new_status == "Closed" and not instance.closed_at:
                data["closed_at"] = now

        return data

    def after_update(self, context, instance):
        from .models import TicketParticipant, TicketActivityLog, TicketStatusHistory

        old_status = getattr(instance, "_pre_update_status", None) or context.metadata.get("prev_ticket_status")
        new_status = instance.ticket_status
        user = getattr(context, "user", None)
        status_changed = bool(old_status and old_status != new_status)

        # 1. If status changed, record history & activity
        if status_changed:
            last_history = TicketStatusHistory.objects.filter(ticket=instance).order_by("-id").first()
            elapsed_sec = 0
            if last_history and last_history.created_at:
                elapsed_sec = int((timezone.now() - last_history.created_at).total_seconds())

            TicketStatusHistory.objects.create(
                ticket=instance,
                from_status=old_status,
                to_status=new_status,
                changed_by=user,
                duration_seconds=max(0, elapsed_sec)
            )

            TicketActivityLog.objects.create(
                ticket=instance,
                action="status_changed",
                performed_by=user,
                details={"from_status": old_status, "to_status": new_status, "duration_seconds": elapsed_sec}
            )

        # 2. If assignee changed
        if instance.assignee:
            TicketParticipant.objects.update_or_create(
                ticket=instance,
                user=instance.assignee,
                defaults={"role": "assignee"}
            )

        # 3. Side effects on_commit (bi-directional task sync & notifications)
        def on_commit_ticket_update():
            try:
                from notifications.models import Notification

                # Bi-directional sync: if ticket resolved/closed, auto-resolve task
                if status_changed and instance.ticket_status in ["Resolved", "Closed"] and instance.linked_task:
                    task = instance.linked_task
                    if task.status not in ["Done", "Completed", "Closed"]:
                        task.status = "Done"
                        task.progress = 100
                        task.save(update_fields=["status", "progress"])

                # Notify participants STRICTLY when status actually changes
                if status_changed:
                    participants = TicketParticipant.objects.filter(ticket=instance, status=1)
                    for p in participants:
                        if p.user != user:
                            Notification.objects.create(
                                recipient=p.user,
                                sender=user,
                                type="ticket_update",
                                title=f"Ticket Updated: {instance.ticket_id}",
                                message=f"Ticket '{instance.title}' status changed to {instance.ticket_status}",
                                path=f"/tickets/{instance.id}"
                            )
            except Exception:
                logger.exception("Error in on_commit_ticket_update side effects")

        transaction.on_commit(on_commit_ticket_update)
        return instance


# ============================================================================
# 2. TICKET COMMENT SERVICE
# ============================================================================

@register_service("ticket_comment")
class TicketCommentService(BaseService):
    def check_permission(self, context):
        if getattr(context.user, "is_superadmin", False):
            return True
        if getattr(context.user, "is_authenticated", False):
            return True
        return None

    def before_create(self, context, data):
        if not data.get("content"):
            raise ValueError("Comment content cannot be empty.")
        if not data.get("ticket") and not data.get("ticket_id"):
            raise ValueError("ticket is required for TicketComment.")

        user = getattr(context, "user", None)
        if user and getattr(user, "is_authenticated", False):
            # Anti-spoofing: author strictly bound to authenticated user
            if not getattr(user, "is_superadmin", False):
                data["author_id"] = user.id
            elif not data.get("author") and not data.get("author_id"):
                data["author_id"] = user.id

        data["status"] = data.get("status", 1)
        return data

    def after_create(self, context, instance):
        from .models import TicketParticipant, TicketActivityLog

        user = instance.author
        ticket = instance.ticket

        # 1. Register commenter as watcher participant
        if user:
            TicketParticipant.objects.get_or_create(
                ticket=ticket,
                user=user,
                defaults={"role": "watcher"}
            )

        # 2. Record activity log
        TicketActivityLog.objects.create(
            ticket=ticket,
            action="comment_added",
            performed_by=user,
            details={"comment_id": instance.id, "is_internal": instance.is_internal}
        )

        # 3. Dynamic ticket status switching
        # If staff comments publicly on an "In Progress" or "Open" ticket, move to "Waiting For Customer"
        if not instance.is_internal and ticket.ticket_status in ["In Progress", "Open"]:
            ticket.ticket_status = "Waiting For Customer"
            ticket.save(update_fields=["ticket_status"])

        # 4. Side effects on_commit (notify ticket participants)
        def on_commit_comment_notify():
            try:
                from notifications.models import Notification
                participants = TicketParticipant.objects.filter(ticket=ticket, status=1)
                for p in participants:
                    if p.user != user:
                        # Skip if internal comment and participant is not staff/admin
                        if instance.is_internal and not getattr(p.user, "is_staff", False) and not getattr(p.user, "is_superadmin", False):
                            continue
                        Notification.objects.create(
                            recipient=p.user,
                            sender=user,
                            type="ticket_comment",
                            title=f"New Comment on {ticket.ticket_id}",
                            message=f"{user.username if user else 'Someone'} commented: {instance.content[:80]}...",
                            path=f"/tickets/{ticket.id}"
                        )
            except Exception:
                logger.exception("Error in on_commit_comment_notify side effects")

        transaction.on_commit(on_commit_comment_notify)
        return instance


# ============================================================================
# 3. TICKET ATTACHMENT SERVICE
# ============================================================================

@register_service("ticket_attachment")
class TicketAttachmentService(BaseService):
    def check_permission(self, context):
        if getattr(context.user, "is_authenticated", False):
            return True
        return None

    def before_create(self, context, data):
        if not data.get("file_url") or not data.get("file_name"):
            raise ValueError("file_url and file_name are required.")

        user = getattr(context, "user", None)
        if user and getattr(user, "is_authenticated", False):
            if not getattr(user, "is_superadmin", False):
                data["uploaded_by_id"] = user.id
            elif not data.get("uploaded_by") and not data.get("uploaded_by_id"):
                data["uploaded_by_id"] = user.id

        data["status"] = data.get("status", 1)
        return data

    def after_create(self, context, instance):
        from .models import TicketActivityLog
        TicketActivityLog.objects.create(
            ticket=instance.ticket,
            action="attachment_uploaded",
            performed_by=instance.uploaded_by,
            details={"file_name": instance.file_name, "file_size": instance.file_size}
        )
        return instance


# ============================================================================
# 4. TICKET ACTIVITY LOG, PARTICIPANT & STATUS HISTORY SERVICES
# ============================================================================

@register_service("ticket_activity_log")
class TicketActivityLogService(BaseService):
    def check_permission(self, context):
        if context.action in ("read", "report", "statistics", "aggregate") and getattr(context.user, "is_authenticated", False):
            return True
        return None


@register_service("ticket_participant")
class TicketParticipantService(BaseService):
    def check_permission(self, context):
        if getattr(context.user, "is_authenticated", False):
            return True
        return None


@register_service("ticket_status_history")
class TicketStatusHistoryService(BaseService):
    def check_permission(self, context):
        if context.action in ("read", "report", "statistics", "aggregate") and getattr(context.user, "is_authenticated", False):
            return True
        return None
