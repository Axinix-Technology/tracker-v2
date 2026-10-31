import logging
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from populate_core.registry import BaseService, register_service
from populate_core.response.exceptions import AuthorizationError

logger = logging.getLogger(__name__)


# ============================================================================
# 1. USER / EMPLOYEE SERVICE
# ============================================================================

@register_service("user")
class UserService(BaseService):
    def check_permission(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return True

        if not getattr(context.user, "is_authenticated", False):
            return None

        # Authenticated users can read the employee directory
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True

        # Non-superadmin cannot create or delete users
        if context.action in ("create", "delete", "bulk-create", "bulk-delete"):
            raise AuthorizationError(
                "Only superadmin users can create or delete employee accounts.",
                code="ADMIN_REQUIRED",
                status_code=403
            )

        # Non-superadmin cannot modify user accounts
        if context.action in ("update", "bulk-update"):
            raise AuthorizationError(
                "Modifying user records requires administrative privileges.",
                code="ADMIN_REQUIRED",
                status_code=403
            )

        return None

    def get_policy_scope(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return Q()
        return Q(is_deleted=False)

    def get_forbidden_fields(self, context):
        # Never project or return passwords in responses
        forbidden = ["password"]
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super:
            # Prevent privilege escalation and tamper with system flags
            forbidden.extend([
                "is_superuser",
                "is_staff",
                "is_superadmin",
                "role",
                "role_id",
                "emp_id",
                "status",
                "is_deleted",
            ])
        return forbidden

    def before_create(self, context, data):
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super:
            raise AuthorizationError(
                "Only superadmin users can create employee accounts.",
                code="ADMIN_REQUIRED",
                status_code=403
            )

        # 1. Password Hashing
        raw_password = data.get("password")
        if raw_password:
            data["password"] = make_password(str(raw_password).strip())
        else:
            # Default unusable/temporary password if omitted
            data["password"] = make_password("Axinix@Temp123")

        # 2. Defaults and Sanitization
        data["status"] = data.get("status", 1)
        data["is_deleted"] = data.get("is_deleted", False)

        # 3. Prevent non-superuser from creating superusers
        if not getattr(context.user, "is_superuser", False):
            data["is_superuser"] = False
            data["is_staff"] = False

        return data

    def before_update(self, context, instance, data):
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super:
            raise AuthorizationError(
                "Modifying user records requires administrative privileges.",
                code="ADMIN_REQUIRED",
                status_code=403
            )

        # Handle password update
        if "password" in data:
            new_pwd = data.pop("password")
            if new_pwd and str(new_pwd).strip():
                data["password"] = make_password(str(new_pwd).strip())

        return data


# ============================================================================
# 2. ROLE SERVICE
# ============================================================================

@register_service("role")
class RoleService(BaseService):
    def check_permission(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return True

        if context.action in ("read", "report", "statistics", "aggregate") and getattr(context.user, "is_authenticated", False):
            return True

        if not is_super:
            raise AuthorizationError(
                "Only superadmin users can manage roles.",
                code="ADMIN_REQUIRED",
                status_code=403
            )
        return None

    def get_policy_scope(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return Q()
        return Q(status=1)

    def before_create(self, context, data):
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super:
            raise AuthorizationError(
                "Only superadmin users can create roles.",
                code="ADMIN_REQUIRED",
                status_code=403
            )
        return data

    def before_update(self, context, instance, data):
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super:
            raise AuthorizationError(
                "Only superadmin users can modify roles.",
                code="ADMIN_REQUIRED",
                status_code=403
            )
        return data

    def before_delete(self, context, instance):
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super:
            raise AuthorizationError(
                "Only superadmin users can delete roles.",
                code="ADMIN_REQUIRED",
                status_code=403
            )
        return instance


# ============================================================================
# 3. MASTER DATA SERVICES
# ============================================================================

class MasterDataService(BaseService):
    """Base service for Master tables: open read for authenticated users, admin-only write."""
    def check_permission(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return True
        if context.action in ("read", "report", "statistics", "aggregate") and getattr(context.user, "is_authenticated", False):
            return True
        if not is_super:
            raise AuthorizationError(
                "Admin privileges required to modify master data records.",
                code="ADMIN_REQUIRED",
                status_code=403
            )
        return None

    def get_policy_scope(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return Q()
        return Q(status=1)

    def before_create(self, context, data):
        if not getattr(context.user, "is_superadmin", False):
            raise AuthorizationError(
                "Admin privileges required to create master data records.",
                code="ADMIN_REQUIRED",
                status_code=403
            )
        return data

    def before_update(self, context, instance, data):
        if not getattr(context.user, "is_superadmin", False):
            raise AuthorizationError(
                "Admin privileges required to update master data records.",
                code="ADMIN_REQUIRED",
                status_code=403
            )
        return data

    def before_delete(self, context, instance):
        if not getattr(context.user, "is_superadmin", False):
            raise AuthorizationError(
                "Admin privileges required to delete master data records.",
                code="ADMIN_REQUIRED",
                status_code=403
            )
        return instance


@register_service("department")
class DepartmentService(MasterDataService):
    pass


@register_service("designation")
class DesignationService(MasterDataService):
    pass


@register_service("company")
class CompanyService(MasterDataService):
    pass


@register_service("client")
class ClientService(MasterDataService):
    pass


@register_service("project_type")
class ProjectTypeService(MasterDataService):
    pass
