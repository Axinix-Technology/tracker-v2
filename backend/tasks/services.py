import datetime
import uuid
import re
from django.db import models, transaction
from django.utils import timezone
from populate_core.registry import BaseService, register_service


# ============================================================================
# 1. TASK TYPE SERVICE
# ============================================================================

@register_service("task_type")
class TaskTypeService(BaseService):
    def check_permission(self, context):
        if context.action == "read" and getattr(context.user, "is_authenticated", False):
            return True
        if getattr(context.user, "is_superadmin", False):
            return True
        return None

    def before_create(self, context, data):
        if not data.get("name"):
            raise ValueError("TaskType name is required.")
        data["isActive"] = data.get("isActive", True)
        return data


# ============================================================================
# 2. SPRINT SERVICE
# ============================================================================

@register_service("sprint")
class SprintService(BaseService):
    def check_permission(self, context):
        if context.action == "read" and getattr(context.user, "is_authenticated", False):
            return True
        if getattr(context.user, "is_superadmin", False):
            return True
        return None

    def before_create(self, context, data):
        if not data.get("name"):
            raise ValueError("Sprint name is required.")

        start_date = data.get("startDate")
        end_date = data.get("endDate")
        if start_date and end_date and str(start_date) > str(end_date):
            raise ValueError("Sprint startDate cannot be after endDate.")

        if hasattr(context, "user") and getattr(context.user, "is_authenticated", False):
            if not data.get("createdBy") and not data.get("createdBy_id"):
                data["createdBy_id"] = context.user.id

        data["state"] = data.get("state", "Upcoming")
        return data

    def before_update(self, context, instance, data):
        start_date = data.get("startDate", instance.startDate)
        end_date = data.get("endDate", instance.endDate)
        if start_date and end_date and str(start_date) > str(end_date):
            raise ValueError("Sprint startDate cannot be after endDate.")

        new_state = data.get("state")
        if new_state == "Completed" and instance.state != "Completed":
            from .models import Task
            completed_points = Task.objects.filter(
                sprintId=instance,
                status__in=["Done", "Completed", "Closed"],
                lifecycle_status=1
            ).aggregate(total=models.Sum("storyPoints"))["total"] or 0.0
            data["velocity"] = float(completed_points)

        return data


# ============================================================================
# 3. MILESTONE SERVICE
# ============================================================================

@register_service("milestone")
class MilestoneService(BaseService):
    def check_permission(self, context):
        if context.action == "read" and getattr(context.user, "is_authenticated", False):
            return True
        if getattr(context.user, "is_superadmin", False):
            return True
        return None

    def before_create(self, context, data):
        if not data.get("title"):
            raise ValueError("Milestone title is required.")
        if not data.get("clientId") and not data.get("clientId_id"):
            raise ValueError("Milestone requires a valid clientId.")
        if not data.get("projectTypeId") and not data.get("projectTypeId_id"):
            raise ValueError("Milestone requires a valid projectTypeId.")

        billing = data.get("billingPercentage")
        if billing is not None:
            billing_val = float(billing)
            if billing_val < 0 or billing_val > 100:
                raise ValueError("Milestone billingPercentage must be between 0 and 100.")

        data["status"] = data.get("status", "Pending")
        return data


# ============================================================================
# 4. TASK SERVICE (CORE JIRA-RIVAL ENGINE)
# ============================================================================

@register_service("task")
class TaskService(BaseService):
    def check_permission(self, context):
        if getattr(context.user, "is_authenticated", False):
            return True
        return None

    def before_create(self, context, data):
        if not data.get("title") and data.get("name"):
            data["title"] = data.pop("name")
        if not data.get("title"):
            raise ValueError("Task title is required.")

        if "priority" in data and "priorityLevel" not in data:
            data["priorityLevel"] = data.pop("priority")
        if "stage" in data and "status" not in data:
            data["status"] = data.pop("stage")
        if "estimated_hours" in data and "estimatedHours" not in data:
            data["estimatedHours"] = data.pop("estimated_hours")

        from .models import Task
        # Auto-generate sequential Jira issue key (e.g. AXN-1, AXN-2)
        last_task = Task.objects.order_by("-id").first()
        next_num = (last_task.id + 1) if last_task else 1
        data["task_key"] = data.get("task_key") or f"AXN-{next_num}"

        # Prevent circular self-parenting on create
        if data.get("parentTask_id") and data.get("parentTask_id") == next_num:
            data.pop("parentTask_id")

        now_iso = timezone.now().isoformat()
        initial_stage = data.get("status", "Backlogs")
        data["stageHistory"] = [{"stage": initial_stage, "enteredAt": now_iso, "duration": 0}]

        user = getattr(context, "user", None)
        if user and not data.get("createdBy") and not data.get("createdBy_id"):
            data["createdBy_id"] = user.id

        if data.get("linkedTicketId") or data.get("linkedTicketId_id"):
            data["isFromTicket"] = True
            tck_id = data.get("linkedTicketId_id") or data.get("linkedTicketId")
            if isinstance(tck_id, (int, str)):
                try:
                    from tickets.models import Ticket
                    tck = Ticket.objects.filter(id=int(tck_id)).first()
                    if tck:
                        data["ticket_snapshot"] = {
                            "ticket_id": tck.ticket_id,
                            "title": tck.title,
                            "priority": getattr(tck, "priority", "Medium"),
                            "ticket_status": getattr(tck, "ticket_status", "Open"),
                        }
                except Exception:
                    pass

        data["status"] = initial_stage
        data["metaStatus"] = data.get("metaStatus", "active")
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        if not data.get("title") and data.get("name"):
            data["title"] = data.pop("name")
        if "priority" in data and "priorityLevel" not in data:
            data["priorityLevel"] = data.pop("priority")
        if "stage" in data and "status" not in data:
            data["status"] = data.pop("stage")
        if "estimated_hours" in data and "estimatedHours" not in data:
            data["estimatedHours"] = data.pop("estimated_hours")
        if data.get("linkedTicketId") or data.get("linkedTicketId_id"):
            data["isFromTicket"] = True
            tck_id = data.get("linkedTicketId_id") or data.get("linkedTicketId")
            if isinstance(tck_id, (int, str)):
                try:
                    from tickets.models import Ticket
                    tck = Ticket.objects.filter(id=int(tck_id)).first()
                    if tck:
                        data["ticket_snapshot"] = {
                            "ticket_id": tck.ticket_id,
                            "title": tck.title,
                            "priority": getattr(tck, "priority", "Medium"),
                            "ticket_status": getattr(tck, "ticket_status", "Open"),
                        }
                except Exception:
                    pass
        elif instance.linkedTicketId and not instance.ticket_snapshot:
            # Ensure existing linked tickets are backfilled into snapshot
            try:
                tck = instance.linkedTicketId
                data["ticket_snapshot"] = {
                    "ticket_id": tck.ticket_id,
                    "title": tck.title,
                    "priority": getattr(tck, "priority", "Medium"),
                    "ticket_status": getattr(tck, "ticket_status", "Open"),
                }
            except Exception:
                pass
        if parent_id and str(parent_id) == str(instance.id):
            raise ValueError("A task cannot be its own parent.")

        new_status = data.get("status")
        if new_status and new_status != instance.status:
            history = list(instance.stageHistory or [])
            now = timezone.now()
            now_iso = now.isoformat()

            if history:
                last_entry = history[-1]
                entered_at_str = last_entry.get("enteredAt")
                if entered_at_str:
                    try:
                        entered_at = datetime.datetime.fromisoformat(entered_at_str)
                        if timezone.is_naive(entered_at):
                            entered_at = timezone.make_aware(entered_at)
                        duration_sec = int((now - entered_at).total_seconds())
                        last_entry["duration"] = max(0, duration_sec)
                    except Exception:
                        pass

            history.append({"stage": new_status, "enteredAt": now_iso, "duration": 0})
            data["stageHistory"] = history

            if new_status in ["Done", "Completed", "Closed"]:
                data["progress"] = 100

        return data

    def after_create(self, context, instance):
        from .models import CommentsThread, EmployeeTaskQueue
        from notifications.models import Notification

        # 1. Initialize empty comments thread
        CommentsThread.objects.get_or_create(taskId=instance, defaults={"comments": []})

        # 2. Enqueue into assignee's personal queue if assignee is present
        if instance.assigneeId:
            queue_obj, _ = EmployeeTaskQueue.objects.get_or_create(employeeId=instance.assigneeId, defaults={"queue": []})
            current_queue = list(queue_obj.queue or [])
            if instance.id not in current_queue:
                current_queue.append(instance.id)
                queue_obj.queue = current_queue
                queue_obj.save()

        # 3. Non-blocking side effects on commit
        def on_commit_task_side_effects():
            try:
                # Notify assignee
                if instance.assigneeId and instance.assigneeId != getattr(context, "user", None):
                    Notification.objects.create(
                        recipient=instance.assigneeId,
                        sender=getattr(context, "user", None),
                        type="task_assignment",
                        title=f"Task Assigned: [{instance.task_key}] {instance.title}",
                        message=f"You have been assigned to task {instance.task_key}",
                        path=f"/tasks/{instance.id}"
                    )
                # Sync linked ticket status if applicable
                if instance.linkedTicketId:
                    from tickets.models import Ticket
                    Ticket.objects.filter(id=instance.linkedTicketId_id).update(ticket_status="In Progress")
            except Exception:
                pass

        transaction.on_commit(on_commit_task_side_effects)
        return instance

    def after_update(self, context, instance):
        from notifications.models import Notification

        def on_commit_task_update():
            try:
                if instance.status in ["Done", "Completed", "Closed"] and instance.linkedTicketId:
                    from tickets.models import Ticket
                    Ticket.objects.filter(id=instance.linkedTicketId_id).update(ticket_status="Resolved", resolved_at=timezone.now())

                # Notify followers
                followers = list(instance.followers.all())
                sender = getattr(context, "user", None)
                for f in followers:
                    if f != sender:
                        Notification.objects.create(
                            recipient=f,
                            sender=sender,
                            type="task_update",
                            title=f"Task Updated: [{instance.task_key}]",
                            message=f"Task status changed to {instance.status}",
                            path=f"/tasks/{instance.id}"
                        )
            except Exception:
                pass

        transaction.on_commit(on_commit_task_update)
        return instance


# ============================================================================
# 5. TIME TRACKER SESSION SERVICE
# ============================================================================

@register_service("time_tracker_session")
class TimeTrackerSessionService(BaseService):
    def check_permission(self, context):
        if getattr(context.user, "is_authenticated", False):
            return True
        return None

    def before_create(self, context, data):
        task_id = data.get("taskId") or data.get("taskId_id")
        if not task_id:
            raise ValueError("TimeTrackerSession requires a valid taskId.")

        from .models import Task, TimeTrackerSession

        user = getattr(context, "user", None)
        user_id = data.get("userId") or data.get("userId_id") or (user.id if user else None)
        if not user_id:
            raise ValueError("TimeTrackerSession requires a valid userId.")
        data["userId_id"] = user_id

        task = Task.objects.filter(id=task_id).first()
        if task:
            if not data.get("projectId") and not data.get("projectId_id") and task.projectTypeId:
                data["projectId_id"] = task.projectTypeId_id
            if not data.get("clientId") and not data.get("clientId_id") and task.clientId:
                data["clientId_id"] = task.clientId_id
            if not data.get("deliveryStageAtStart"):
                data["deliveryStageAtStart"] = task.deliveryStage or task.status

        # Auto-pause/stop any currently active sessions for this user
        active_sessions = TimeTrackerSession.objects.filter(
            userId_id=user_id,
            status="active",
            lifecycle_status=1
        )
        now = timezone.now()
        for session in active_sessions:
            session.status = "paused"
            pauses = list(session.pauses or [])
            pauses.append({"pausedAt": now.isoformat(), "resumedAt": None, "duration": 0})
            session.pauses = pauses
            session.save()

        data["startTime"] = data.get("startTime") or now
        data["status"] = "active"
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_status = data.get("status")
        now = timezone.now()

        if new_status == "paused" and instance.status == "active":
            pauses = list(instance.pauses or [])
            pauses.append({"pausedAt": now.isoformat(), "resumedAt": None, "duration": 0})
            data["pauses"] = pauses

        elif new_status == "active" and instance.status == "paused":
            pauses = list(instance.pauses or [])
            if pauses and pauses[-1].get("resumedAt") is None:
                paused_at_str = pauses[-1].get("pausedAt")
                if paused_at_str:
                    try:
                        paused_at = datetime.datetime.fromisoformat(paused_at_str)
                        if timezone.is_naive(paused_at):
                            paused_at = timezone.make_aware(paused_at)
                        pause_sec = int((now - paused_at).total_seconds())
                        pauses[-1]["resumedAt"] = now.isoformat()
                        pauses[-1]["duration"] = max(0, pause_sec)
                    except Exception:
                        pass
            data["pauses"] = pauses

        elif new_status in ["completed", "stopped"] and instance.status != "completed":
            data["endTime"] = now
            start = instance.startTime
            gross_seconds = int((now - start).total_seconds()) if start else 0

            # Calculate total paused duration
            total_pause_sec = 0
            pauses = list(data.get("pauses", instance.pauses or []))
            for p in pauses:
                total_pause_sec += p.get("duration", 0)

            net_worked_seconds = max(0, gross_seconds - total_pause_sec)
            data["duration"] = net_worked_seconds

            rate = float(data.get("employeeHourlyRate", instance.employeeHourlyRate or 0.0))
            if rate > 0:
                data["productionCost"] = round((net_worked_seconds / 3600.0) * rate, 2)

        return data

    def after_create(self, context, instance):
        from .models import Task
        Task.objects.filter(id=instance.taskId_id).update(
            activeJobSessionId=instance.id
        )
        task = Task.objects.filter(id=instance.taskId_id).first()
        if task and task.status in ["Backlogs", "To Do"]:
            task.status = "In Progress"
            task.save()
        return instance

    def after_update(self, context, instance):
        from .models import Task, TimeTrackerSession
        if instance.status in ["completed", "stopped"]:
            Task.objects.filter(id=instance.taskId_id, activeJobSessionId=instance.id).update(
                activeJobSessionId=None
            )
            # Recompute total actualHours on commit
            def on_commit_update_actual_hours():
                try:
                    total_sec = TimeTrackerSession.objects.filter(
                        taskId_id=instance.taskId_id,
                        status__in=["completed", "stopped"],
                        lifecycle_status=1
                    ).aggregate(total=models.Sum("duration"))["total"] or 0
                    Task.objects.filter(id=instance.taskId_id).update(
                        actualHours=round(total_sec / 3600.0, 2)
                    )
                except Exception:
                    pass

            transaction.on_commit(on_commit_update_actual_hours)
        return instance


# ============================================================================
# 6. EMPLOYEE TASK QUEUE SERVICE
# ============================================================================

@register_service("employee_task_queue")
class EmployeeTaskQueueService(BaseService):
    def check_permission(self, context):
        if getattr(context.user, "is_authenticated", False):
            return True
        return None

    def before_update(self, context, instance, data):
        new_queue = data.get("queue")
        if new_queue is not None:
            # Deduplicate preserving order
            seen = set()
            deduped = []
            for item in new_queue:
                if item not in seen:
                    seen.add(item)
                    deduped.append(item)
            data["queue"] = deduped
        return data


# ============================================================================
# 7. EMPLOYEE TASK QUEUE REQUEST SERVICE
# ============================================================================

@register_service("employee_task_queue_request")
class EmployeeTaskQueueRequestService(BaseService):
    def check_permission(self, context):
        if getattr(context.user, "is_authenticated", False):
            return True
        return None

    def before_create(self, context, data):
        if not data.get("taskId") and not data.get("taskId_id"):
            raise ValueError("taskId is required for task queue request.")
        user = getattr(context, "user", None)
        if user and not data.get("employeeId") and not data.get("employeeId_id"):
            data["employeeId_id"] = user.id
        data["status"] = "Pending"
        return data


# ============================================================================
# 8. COMMENTS THREAD SERVICE
# ============================================================================

@register_service("comments_thread")
class CommentsThreadService(BaseService):
    def check_permission(self, context):
        if getattr(context.user, "is_authenticated", False):
            return True
        return None

    def before_update(self, context, instance, data):
        incoming_comments = data.get("comments")
        if incoming_comments is not None:
            now_iso = timezone.now().isoformat()
            user = getattr(context, "user", None)
            for c in incoming_comments:
                if not c.get("id"):
                    c["id"] = str(uuid.uuid4())
                if not c.get("createdAt"):
                    c["createdAt"] = now_iso
                if not c.get("userId") and user:
                    c["userId"] = user.id
            data["comments"] = incoming_comments
        return data

    def after_update(self, context, instance):
        from notifications.models import Notification
        from users.models import User

        def on_commit_notify_mentions():
            try:
                comments = instance.comments or []
                if not comments:
                    return
                latest_comment = comments[-1]
                text = latest_comment.get("text", "")
                mentioned_usernames = re.findall(r"@([a-zA-Z0-9_\.]+)", text)
                if mentioned_usernames:
                    users_to_notify = User.objects.filter(username__in=mentioned_usernames)
                    sender = getattr(context, "user", None)
                    for user in users_to_notify:
                        if user != sender:
                            Notification.objects.create(
                                recipient=user,
                                sender=sender,
                                type="comment_mention",
                                title=f"Mentioned in Task #{instance.taskId_id}",
                                message=f"{sender.username if sender else 'Someone'} mentioned you in a task comment.",
                                path=f"/tasks/{instance.taskId_id}"
                            )
            except Exception:
                pass

        transaction.on_commit(on_commit_notify_mentions)
        return instance


# ============================================================================
# 9. TODO SERVICE
# ============================================================================

@register_service("todo")
class TodoService(BaseService):
    def check_permission(self, context):
        if getattr(context.user, "is_authenticated", False):
            return True
        return None

    def before_create(self, context, data):
        if not data.get("text"):
            raise ValueError("Todo text is required.")
        if not data.get("employeeId") and not data.get("employeeId_id"):
            user = getattr(context, "user", None)
            if user:
                data["employeeId_id"] = user.id
            else:
                raise ValueError("employeeId is required.")
        return data


# ============================================================================
# 10. DAILY ACTIVITY SERVICE
# ============================================================================

@register_service("daily_activity")
class DailyActivityService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        # Authenticated team members can log and read their daily activities
        if context.action in ("read", "create", "report", "statistics", "aggregate"):
            return True

        # Defer updates and deletions to PolicyEngine (prevent arbitrary tampering/deletion)
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return models.Q(lifecycle_status=1)

        from populate_core.policy.engine import PolicyEngine
        # Scrum masters, leads, and PMs with read capability see all team activities
        if PolicyEngine.has_capability(context, "daily_activity.read") or PolicyEngine.has_capability(context, "daily_activity.all"):
            return models.Q(lifecycle_status=1)

        # Standard employee fallback: view own or assigned activities
        return models.Q(lifecycle_status=1) & (models.Q(user=context.user) | models.Q(assigned_to=context.user))

    def before_create(self, context, data):
        target_user = data.get("user") or data.get("user_id")

        from populate_core.policy.engine import PolicyEngine
        has_manage = context.is_superadmin or PolicyEngine.has_capability(context, "daily_activity.create")

        if not has_manage or not target_user:
            data["user_id"] = context.user.id
        else:
            data["user_id"] = target_user if not hasattr(target_user, "id") else target_user.id

        if not data.get("activity"):
            raise ValueError("activity description is required.")

        data["date"] = data.get("date") or timezone.now().date()
        data["status"] = data.get("status", "Pending")
        data["meta_status"] = data.get("meta_status", "active")
        data["lifecycle_status"] = 1
        return data
