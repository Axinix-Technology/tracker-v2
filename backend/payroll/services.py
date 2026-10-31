import datetime
import logging
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from populate_core.registry import BaseService, register_service
from populate_core.response.exceptions import AuthorizationError

logger = logging.getLogger(__name__)


# ============================================================================
# 1. SALARY STRUCTURE SERVICE
# ============================================================================

@register_service("salary_structure")
class SalaryStructureService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        # Defer read, create, update to PolicyEngine (AccessPolicy & ABAC conditions)
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()

        from populate_core.policy.engine import PolicyEngine
        # Finance/HR managers with read capability see all active structures
        if PolicyEngine.has_capability(context, "salary_structure.read") or PolicyEngine.has_capability(context, "salary_structure.all"):
            return Q(status=1)

        # Standard employee fallback: only see their own salary structure
        return Q(employee=context.user, status=1)

    def before_create(self, context, data):
        from .models import SalaryStructure

        target_emp_id = data.get("employee") or data.get("employee_id") or data.get("employeeId")
        if not target_emp_id:
            raise ValueError("employee is required.")

        emp_id = target_emp_id if not hasattr(target_emp_id, "id") else target_emp_id.id
        data["employee_id"] = emp_id

        eff_from = data.get("effective_from") or data.get("effectiveFrom")
        if not eff_from:
            raise ValueError("effective_from date is required.")

        data["effective_from"] = eff_from
        data["created_by_id"] = getattr(context.user, "id", None)

        # 1. Versioning: Find latest version and increment
        latest = SalaryStructure.objects.filter(employee_id=emp_id).order_by("-version").first()
        data["version"] = (latest.version + 1) if latest else 1

        # 2. Close previous open version
        if latest and latest.effective_to is None:
            eff_from_date = (
                datetime.date.fromisoformat(str(eff_from)[:10])
                if isinstance(eff_from, str)
                else eff_from
            )
            prev_end = eff_from_date - datetime.timedelta(days=1)
            latest.effective_to = prev_end
            latest.save()

        data["status"] = 1
        return data

    def before_update(self, context, instance, data):
        # Prevent mutating immutable historical fields
        immutable_fields = ["employee", "employee_id", "version", "effective_from"]
        for f in immutable_fields:
            if f in data and str(data[f]) != str(getattr(instance, f, None)):
                raise ValueError(f"Field '{f}' is immutable once a salary structure version is registered.")
        return data


# ============================================================================
# 2. PAYROLL RUN SERVICE
# ============================================================================

@register_service("payroll_run")
class PayrollRunService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        # Defer execution and access to PolicyEngine (Finance HR AccessPolicy)
        return None

    def get_policy_scope(self, context):
        return Q(status=1)

    def before_create(self, context, data):
        from .models import PayrollRun

        month = data.get("month")
        year = data.get("year")
        if not month or not year:
            raise ValueError("month and year are required for a payroll run.")

        # Check if completed run already exists for this month/year
        completed_run = PayrollRun.objects.filter(
            month=month,
            year=year,
            run_status__in=["Approved", "Paid"],
            status=1
        ).exists()

        if completed_run:
            raise ValueError(f"A payroll run for {month}/{year} is already Approved/Paid. Subsequent runs are blocked.")

        data["initiated_by_id"] = getattr(context.user, "id", None)
        data["run_status"] = "Draft"
        data["status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_status = data.get("run_status")
        now = timezone.now()

        # Enforce valid state transitions
        valid_transitions = {
            "Draft": ["Processing", "Computed"],
            "Processing": ["Computed", "Draft"],
            "Computed": ["Approved", "Draft"],
            "Approved": ["Paid"],
            "Paid": []
        }

        if new_status and new_status != instance.run_status:
            allowed = valid_transitions.get(instance.run_status, [])
            if new_status not in allowed:
                raise ValueError(f"Invalid state transition from {instance.run_status} to {new_status}.")

            if new_status == "Approved":
                data["approved_by_id"] = getattr(context.user, "id", None)
                data["approved_at"] = now
            elif new_status == "Paid":
                data["paid_at"] = now

        return data


# ============================================================================
# 3. PAYROLL (INDIVIDUAL PAYSLIP) SERVICE
# ============================================================================

@register_service("payroll")
class PayrollService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        # Defer payroll generation/modification/reading to PolicyEngine
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()

        from populate_core.policy.engine import PolicyEngine
        # Finance/HR managers with payroll read capability see all payslips
        if PolicyEngine.has_capability(context, "payroll.read") or PolicyEngine.has_capability(context, "payroll.all"):
            return Q(status=1)

        # Authenticated employees only see their own payslips
        return Q(employee=context.user, status=1)

    def before_create(self, context, data):
        from .models import Payroll

        emp_id = data.get("employee") or data.get("employee_id") or data.get("employeeId")
        month = data.get("month")
        year = data.get("year")

        if not emp_id or not month or not year:
            raise ValueError("employee, month, and year are required.")

        data["employee_id"] = emp_id if not hasattr(emp_id, "id") else emp_id.id
        data["month"] = int(month)
        data["year"] = int(year)

        # Check existing payroll
        existing = Payroll.objects.filter(
            employee_id=data["employee_id"],
            month=data["month"],
            year=data["year"],
            status=1
        ).first()

        if existing and existing.payroll_status in ["Approved", "Paid"]:
            raise ValueError(f"Payroll for employee #{data['employee_id']} for {month}/{year} is already {existing.payroll_status}. Recomputation blocked.")

        data["processed_by_id"] = getattr(context.user, "id", None)
        data["processed_at"] = timezone.now()
        data["payroll_status"] = data.get("payroll_status", "Draft")
        data["status"] = 1
        return data

    def before_update(self, context, instance, data):
        # Frozen field protection: once Approved, financial figures cannot be edited
        if instance.payroll_status in ["Approved", "Paid"]:
            frozen_fields = [
                "gross_salary", "net_salary", "earned_breakdown", "deduction_breakdown",
                "working_days", "present_days", "lop_days", "overtime_pay"
            ]
            for f in frozen_fields:
                if f in data and str(data[f]) != str(getattr(instance, f, None)):
                    raise ValueError(f"Field '{f}' is frozen because payroll is already {instance.payroll_status}.")

        new_status = data.get("payroll_status")
        if new_status and new_status != instance.payroll_status:
            now = timezone.now()
            if new_status == "Approved":
                data["approved_by_id"] = getattr(context.user, "id", None)
                data["approved_at"] = now
                data["frozen_at"] = now
            elif new_status == "Paid":
                data["paid_at"] = now

        return data


# ============================================================================
# 4. EXPENSE SERVICE
# ============================================================================

@register_service("expense")
class ExpenseService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        # Employees can submit reimbursement expenses
        if context.action == "create":
            return True

        # Defer approval/reimbursement updates and reads to PolicyEngine
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()

        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "expense.read") or PolicyEngine.has_capability(context, "expense.all"):
            return Q(status=1)

        # Standard employees can view their own submitted reimbursement expenses
        return Q(employee=context.user, status=1)

    def before_create(self, context, data):
        target_emp = data.get("employee") or data.get("employee_id") or data.get("employeeId")

        from populate_core.policy.engine import PolicyEngine
        has_manage = context.is_superadmin or PolicyEngine.has_capability(context, "expense.create")

        if not has_manage or not target_emp:
            emp_pk = context.user.id
        else:
            emp_pk = target_emp if not hasattr(target_emp, "id") else target_emp.id

        data["employee_id"] = emp_pk

        client_id = data.get("client") or data.get("client_id") or data.get("clientId")
        if not client_id:
            raise ValueError("client is required for expense entry.")
        data["client_id"] = client_id if not hasattr(client_id, "id") else client_id.id

        date_val = data.get("date")
        if not date_val:
            raise ValueError("date is required.")

        date_str = str(date_val)[:10]
        data["date"] = date_str
        data["expense_period"] = date_str[:7]  # 'YYYY-MM'

        # Auto-compute day_total from expenses list
        items = list(data.get("expenses") or [])
        total_amt = sum(float(it.get("amount", 0.0)) for it in items)
        data["day_total"] = round(total_amt, 2)
        data["total_expenses"] = len(items)

        data["expense_status"] = "pending"
        data["meta_status"] = "active"
        data["submitted_at"] = timezone.now()
        data["status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_status = data.get("expense_status")

        if new_status and new_status != instance.expense_status:
            now = timezone.now()
            if new_status == "approved":
                data["approved_by_id"] = context.user.id
                data["approved_at"] = now
            elif new_status == "rejected":
                data["rejected_by_id"] = context.user.id
                data["rejected_at"] = now
            elif new_status == "reimbursed":
                data["reimbursed_by_id"] = context.user.id
                data["reimbursed_at"] = now

        # Recompute day_total if expenses list is updated
        if "expenses" in data:
            items = list(data.get("expenses") or [])
            data["day_total"] = round(sum(float(it.get("amount", 0.0)) for it in items), 2)
            data["total_expenses"] = len(items)

        return data
