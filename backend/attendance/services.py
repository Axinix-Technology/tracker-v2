import datetime
from django.db import models, transaction
from populate_core.registry import BaseService, register_service


@register_service("attendance")
class AttendanceService(BaseService):
    def check_permission(self, context):
        if context.action == "read" and getattr(context.user, "is_authenticated", False):
            return True
        return None


@register_service("leave")
class LeaveService(BaseService):
    def before_create(self, context, data):
        start_date_raw = data.get("startDate")
        end_date_raw = data.get("endDate")
        if not start_date_raw or not end_date_raw:
            raise ValueError("startDate and endDate are required.")

        start_date = (
            datetime.date.fromisoformat(str(start_date_raw)[:10])
            if isinstance(start_date_raw, str)
            else start_date_raw
        )
        end_date = (
            datetime.date.fromisoformat(str(end_date_raw)[:10])
            if isinstance(end_date_raw, str)
            else end_date_raw
        )

        if end_date < start_date:
            raise ValueError("End date must be on or after start date.")

        from .models import Leave, LeaveTransaction

        emp_id = data.get("employeeId") or getattr(context.user, "id", None)
        if not emp_id:
            raise ValueError("employeeId is required.")
        data["employeeId_id"] = emp_id

        # Check for overlapping active leaves
        overlapping = Leave.objects.filter(
            employeeId_id=emp_id,
            status__in=["Pending", "Approved"],
            startDate__lte=end_date,
            endDate__gte=start_date
        ).exists()

        if overlapping:
            raise ValueError("An overlapping leave request already exists for this date range.")

        # Calculate total days
        total_days = (end_date - start_date).days + 1
        data["totalDays"] = float(total_days)
        data["status"] = data.get("status", "Pending")

        return data

    def after_update(self, context, instance):
        # When leave is approved, debit leave balance and update attendance
        if instance.status == "Approved":
            from .models import LeaveTransaction, Attendance
            with transaction.atomic():
                # Avoid duplicate debits
                already_debited = LeaveTransaction.objects.filter(
                    sourceId=instance.id,
                    sourceModel="leaves",
                    type="LEAVE_DEBIT"
                ).exists()

                if not already_debited:
                    LeaveTransaction.objects.create(
                        employeeId=instance.employeeId,
                        leaveTypeId=instance.leaveTypeId,
                        type="LEAVE_DEBIT",
                        sourceId=instance.id,
                        sourceModel="leaves",
                        quantity=-abs(instance.totalDays),
                        description=f"Approved leave from {instance.startDate} to {instance.endDate}"
                    )

                # Sync attendance records to "On Leave"
                curr_date = instance.startDate
                while curr_date <= instance.endDate:
                    Attendance.objects.update_or_create(
                        employee=instance.employeeId,
                        date=curr_date,
                        defaults={"status": "On Leave"}
                    )
                    curr_date += datetime.timedelta(days=1)

        return instance


@register_service("regularization")
class RegularizationService(BaseService):
    def before_create(self, context, data):
        att_id = data.get("attendanceId") or data.get("attendanceId_id")
        if not att_id:
            raise ValueError("attendanceId is required for punch regularization.")

        from .models import Regularization
        pending = Regularization.objects.filter(
            attendanceId_id=att_id,
            status="Pending"
        ).exists()

        if pending:
            raise ValueError("A pending regularization request already exists for this attendance record.")

        data["status"] = "Pending"
        return data

    def after_update(self, context, instance):
        if instance.status == "Approved" and instance.attendanceId:
            att = instance.attendanceId
            att.check_in = instance.requestedCheckIn
            att.check_out = instance.requestedCheckOut
            att.status = "Present"
            att.save()

        return instance


@register_service("comp_off_request")
class CompOffService(BaseService):
    def after_update(self, context, instance):
        if instance.status == "Approved":
            from .models import LeaveTransaction
            with transaction.atomic():
                already_credited = LeaveTransaction.objects.filter(
                    sourceId=instance.id,
                    sourceModel="comp_off_requests",
                    type="COMPOFF_CREDIT"
                ).exists()

                if not already_credited:
                    expiry = instance.expiryDate or (instance.workedDate + datetime.timedelta(days=90))
                    LeaveTransaction.objects.create(
                        employeeId=instance.employeeId,
                        type="COMPOFF_CREDIT",
                        sourceId=instance.id,
                        sourceModel="comp_off_requests",
                        quantity=1.0,
                        expiryDate=expiry,
                        description=f"Comp-off credit for worked date: {instance.workedDate}"
                    )

        return instance


@register_service("wfh_request")
class WFHService(BaseService):
    def after_update(self, context, instance):
        if instance.status == "Approved":
            from .models import Attendance
            curr_date = instance.startDate
            while curr_date <= instance.endDate:
                Attendance.objects.update_or_create(
                    employee=instance.employeeId,
                    date=curr_date,
                    defaults={"status": "Work From Home"}
                )
                curr_date += datetime.timedelta(days=1)

        return instance


# ============================================================================
# 6. PERMISSION & HOLIDAY OVERRIDE SERVICES
# ============================================================================

@register_service("permission_transaction")
class PermissionTransactionService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        if context.action == "create":
            return True

        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return None

        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "permission_transaction.read") or PolicyEngine.has_capability(context, "permission_transaction.all"):
            return models.Q(lifecycle_status=1)

        return models.Q(employee=context.user, lifecycle_status=1)

    def before_create(self, context, data):
        target_emp_id = data.get("employee") or data.get("employee_id") or data.get("employeeId")

        from populate_core.policy.engine import PolicyEngine
        has_manage = context.is_superadmin or PolicyEngine.has_capability(context, "permission_transaction.create")

        if not has_manage or not target_emp_id:
            emp_pk = context.user.id
        else:
            emp_pk = target_emp_id if not hasattr(target_emp_id, "id") else target_emp_id.id

        data["employee_id"] = emp_pk

        if not data.get("date"):
            raise ValueError("date is required for permission transaction.")
        if not data.get("duration_minutes") and not data.get("durationMinutes"):
            raise ValueError("duration_minutes is required.")

        data["duration_minutes"] = data.get("duration_minutes") or data.get("durationMinutes")
        data["status"] = data.get("status", "AutoConsumed")
        data["lifecycle_status"] = 1
        return data

    def after_create(self, context, instance):
        # Auto-debit permission balance for employee for this year/month
        # Note: after_create executes within create.py's atomic transaction
        if instance.status in ("Approved", "AutoConsumed"):
            from .models import PermissionBalance
            tx_date = instance.date
            hours_debited = instance.duration_minutes / 60.0

            bal, created = PermissionBalance.objects.get_or_create(
                employee=instance.employee,
                year=tx_date.year,
                month=tx_date.month,
                defaults={
                    "granted_hours": 2.0,
                    "used_hours": 0.0,
                    "remaining_hours": 2.0,
                    "status": 1
                }
            )
            bal.used_hours = float(bal.used_hours) + hours_debited
            bal.remaining_hours = max(0.0, float(bal.granted_hours) + float(bal.carried_forward_hours) - bal.used_hours)
            bal.save()

        return instance


@register_service("permission_balance")
class PermissionBalanceService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return None

        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "permission_balance.read") or PolicyEngine.has_capability(context, "permission_balance.all"):
            return models.Q(status=1)

        return models.Q(employee=context.user, status=1)


@register_service("holiday_override")
class HolidayOverrideService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        if context.action in ("read", "report", "statistics", "aggregate"):
            return True

        return None
