import logging
from django.db.models import Q
from django.utils import timezone
from populate_core.registry import BaseService, register_service
from populate_core.response.exceptions import AuthorizationError

logger = logging.getLogger(__name__)


# ============================================================================
# 1. EMPLOYEE DOCUMENT SERVICE
# ============================================================================

@register_service("employee_document")
class EmployeeDocumentService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        # Employees can upload their own verification documents
        if context.action == "create":
            return True

        # Defer read, update, delete to PolicyEngine (AccessPolicy & ABAC conditions)
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()

        from populate_core.policy.engine import PolicyEngine
        # If caller holds administrative or read capability, grant organization-wide active scope
        if PolicyEngine.has_capability(context, "employee_document.read") or PolicyEngine.has_capability(context, "employee_document.all"):
            return Q(lifecycle_status=1)

        # Standard employee self-service fallback: strictly scoped to own documents
        return Q(employee=context.user, lifecycle_status=1)

    def before_create(self, context, data):
        target_emp_id = data.get("employee") or data.get("employee_id") or data.get("employeeId")

        from populate_core.policy.engine import PolicyEngine
        has_manage = context.is_superadmin or PolicyEngine.has_capability(context, "employee_document.create")

        # Non-managers cannot upload documents on behalf of other employees
        if not has_manage or not target_emp_id:
            emp_pk = context.user.id
        else:
            emp_pk = target_emp_id if not hasattr(target_emp_id, "id") else target_emp_id.id

        data["employee_id"] = emp_pk

        if not data.get("document_type"):
            raise ValueError("document_type is required.")
        if not data.get("file_url"):
            raise ValueError("file_url is required.")

        data["status"] = "Pending"
        data["uploaded_at"] = timezone.now()
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_status = data.get("status")

        # Status transition (Approved / Rejected) records approving user
        if new_status and new_status != instance.status:
            if new_status in ("Approved", "Rejected"):
                data["approved_by_id"] = context.user.id

        return data


# ============================================================================
# 2. EMPLOYEE LIFECYCLE HISTORY SERVICE
# ============================================================================

@register_service("employee_lifecycle_history")
class EmployeeLifecycleHistoryService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        # Defer all access to PolicyEngine
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()

        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "employee_lifecycle_history.read") or PolicyEngine.has_capability(context, "employee_lifecycle_history.all"):
            return Q(lifecycle_status=1, is_deleted=False)

        # Standard employees can view their own career progression timeline
        return Q(employee=context.user, lifecycle_status=1, is_deleted=False)

    def before_create(self, context, data):
        target_emp_id = data.get("employee") or data.get("employee_id") or data.get("employeeId")
        if not target_emp_id:
            raise ValueError("employee is required.")

        emp_pk = target_emp_id if not hasattr(target_emp_id, "id") else target_emp_id.id
        data["employee_id"] = emp_pk
        data["changed_by_id"] = getattr(context.user, "id", None)
        data["effective_date"] = data.get("effective_date") or timezone.now().date()
        data["lifecycle_status"] = 1
        data["is_deleted"] = False
        return data


# ============================================================================
# 3. HR POLICY SERVICE
# ============================================================================

@register_service("hr_policy")
class HRPolicyService(BaseService):
    def check_permission(self, context):
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        if context.is_superadmin:
            return True

        # All authenticated employees can read published company policies
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True

        # Allow employees to submit policy self-acknowledgments
        if context.action == "update" and isinstance(getattr(context, "body", None), dict):
            if "new_acknowledgment" in context.body:
                return True

        # Defer policy authoring/updating to PolicyEngine for HR roles
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()

        from populate_core.policy.engine import PolicyEngine
        # HR managers with policy capability can view drafts and archived policies
        if PolicyEngine.has_capability(context, "hr_policy.update") or PolicyEngine.has_capability(context, "hr_policy.all"):
            return Q(lifecycle_status=1)

        # Standard employees can only view active/published policies
        return Q(lifecycle_status=1) & (Q(status="Active") | Q(is_public=True))

    def before_create(self, context, data):
        if not data.get("title"):
            raise ValueError("title is required for HR policy.")
        if not data.get("content"):
            raise ValueError("content is required for HR policy.")

        data["created_by_id"] = context.user.id
        data["lifecycle_status"] = 1
        data["status"] = data.get("status", "Draft")
        data["effective_date"] = data.get("effective_date") or timezone.now().date()
        return data

    def before_update(self, context, instance, data):
        new_acknowledgment = data.get("new_acknowledgment")

        from populate_core.policy.engine import PolicyEngine
        is_manager = context.is_superadmin or PolicyEngine.has_capability(context, "hr_policy.update")

        # Employee self-acknowledgment security guard: strictly sanitize payload to ONLY the acknowledgment
        if new_acknowledgment and not is_manager:
            ack_entry = {
                "employeeId": context.user.id,
                "acknowledgedAt": timezone.now().isoformat(),
                "ipAddress": getattr(context, "ip_address", None)
            }
            existing_acks = list(instance.acknowledgments or [])
            if not any(a.get("employeeId") == context.user.id for a in existing_acks):
                existing_acks.append(ack_entry)

            # Sanitize: Strip all other fields to prevent unauthorized policy tampering
            data.clear()
            data["acknowledgments"] = existing_acks
            return data

        if new_acknowledgment and is_manager:
            ack_entry = {
                "employeeId": context.user.id,
                "acknowledgedAt": timezone.now().isoformat(),
                "ipAddress": getattr(context, "ip_address", None)
            }
            existing_acks = list(instance.acknowledgments or [])
            if not any(a.get("employeeId") == context.user.id for a in existing_acks):
                existing_acks.append(ack_entry)
            data["acknowledgments"] = existing_acks
            data.pop("new_acknowledgment", None)

        new_status = data.get("status")
        if new_status == "Active" and instance.status != "Active":
            data["approved_by_id"] = context.user.id
            data["approved_at"] = timezone.now()

        return data


# ============================================================================
# 4. USER OVERRIDE SERVICE
# ============================================================================

@register_service("user_override")
class UserOverrideService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        # Authenticated users can read their own UI capability overrides
        if context.action == "read":
            return True

        # Defer override creation/updates to PolicyEngine
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()

        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "user_override.read") or PolicyEngine.has_capability(context, "user_override.all"):
            return Q()

        return Q(user=context.user)
