import logging
from django.db import models
from django.db.models import Q
from django.utils import timezone
from populate_core.registry import BaseService, register_service
from populate_core.response.exceptions import AuthorizationError, ValidationError, NotFoundError

logger = logging.getLogger("control_plane.services")


# ============================================================================
# 1. TENANT SERVICE
# ============================================================================

@register_service("tenant")
class TenantService(BaseService):
    def check_permission(self, context):
        is_root = getattr(context, "is_root_admin", False) or getattr(getattr(context, "user", None), "is_root_admin", False)
        if is_root:
            return True
        user = getattr(context, "user", None)
        user_plane = getattr(user, "plane", "client")
        if user_plane == "platform":
            role_id = getattr(getattr(user, "role", None), "role_id", "")
            if role_id in ("root_admin", "superadmin"):
                return True
            if role_id == "management_viewer":
                if context.action in ("read", "report", "statistics", "aggregate"):
                    return True
                raise AuthorizationError("Management Viewer has read-only access to tenants.", code="READ_ONLY_ROLE", status_code=403)
        if not user or not getattr(user, "is_authenticated", False):
            # Allow public subdomain lookup
            if context.action in ("read", "report", "statistics", "aggregate"):
                return True
            return False
        # Client users: cannot create, update, or delete tenants
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True
        raise AuthorizationError("Only Platform Root Admin can provision or mutate tenants.", code="ROOT_ADMIN_REQUIRED", status_code=403)

    def get_policy_scope(self, context):
        is_root = getattr(context, "is_root_admin", False) or getattr(getattr(context, "user", None), "is_root_admin", False)
        if is_root:
            return Q()
        user = getattr(context, "user", None)
        if getattr(user, "plane", "client") == "platform":
            return Q()
        return Q(status="Active", lifecycle_status=1)

    def before_create(self, context, data):
        if not data.get("name"):
            raise ValueError("Tenant name is required.")
        if not data.get("subdomain"):
            raise ValueError("Tenant subdomain is required.")

        subdomain = str(data["subdomain"]).strip().lower().replace(" ", "-")
        data["subdomain"] = subdomain

        if not data.get("tenant_id"):
            data["tenant_id"] = subdomain

        if not data.get("database_name"):
            data["database_name"] = f"tracker_{subdomain.replace('-', '_')}"

        data["status"] = data.get("status", "Active")
        data["lifecycle_status"] = 1
        return data


# ============================================================================
# 2. USER LOGIN SERVICE (ROUTING DIRECTORY)
# ============================================================================

@register_service("user_login")
class UserLoginService(BaseService):
    def check_permission(self, context):
        is_root = getattr(context, "is_root_admin", False) or getattr(getattr(context, "user", None), "is_root_admin", False)
        if is_root:
            return True
        user = getattr(context, "user", None)
        if getattr(user, "plane", "client") == "platform":
            return True
        raise AuthorizationError("Access to user logins directory is restricted to Platform Operators.", code="PLATFORM_ACCESS_FORBIDDEN", status_code=403)

    def get_policy_scope(self, context):
        return Q(is_active=True, lifecycle_status=1)


# ============================================================================
# 3. MODULE SERVICE (GLOBAL ENTITLEMENTS)
# ============================================================================

@register_service("module")
class ModuleService(BaseService):
    def check_permission(self, context):
        is_root = getattr(context, "is_root_admin", False) or getattr(getattr(context, "user", None), "is_root_admin", False)
        if is_root:
            return True
        user = getattr(context, "user", None)
        user_plane = getattr(user, "plane", "client")
        if user_plane == "platform":
            role_id = getattr(getattr(user, "role", None), "role_id", "")
            if role_id in ("root_admin", "superadmin"):
                return True
            if role_id == "management_viewer":
                if context.action in ("read", "report", "statistics", "aggregate"):
                    return True
                raise AuthorizationError("Management Viewer has read-only access to modules.", code="READ_ONLY_ROLE", status_code=403)
        raise AuthorizationError("Access to the global module catalog is restricted to Platform Operators.", code="PLATFORM_ACCESS_FORBIDDEN", status_code=403)

    def get_policy_scope(self, context):
        return Q(is_active=True, lifecycle_status=1)

    def before_create(self, context, data):
        if not data.get("module_id"):
            raise ValueError("module_id is required.")
        if not data.get("name"):
            raise ValueError("name is required.")

        data["module_id"] = str(data["module_id"]).strip().lower()
        data["is_active"] = data.get("is_active", True)
        data["lifecycle_status"] = 1
        return data


# ============================================================================
# 4. PROVISIONING RUN SERVICE
# ============================================================================

@register_service("provisioning_run")
class ProvisioningRunService(BaseService):
    def check_permission(self, context):
        is_root = getattr(context, "is_root_admin", False) or getattr(getattr(context, "user", None), "is_root_admin", False)
        if is_root:
            return True
        user = getattr(context, "user", None)
        user_plane = getattr(user, "plane", "client")
        if user_plane == "platform":
            role_id = getattr(getattr(user, "role", None), "role_id", "")
            if role_id in ("root_admin", "superadmin"):
                return True
            if role_id == "management_viewer":
                if context.action in ("read", "report", "statistics", "aggregate"):
                    return True
                raise AuthorizationError("Management Viewer has read-only access to provisioning runs.", code="READ_ONLY_ROLE", status_code=403)
        raise AuthorizationError("Access to provisioning runs is restricted to Platform Operators.", code="PLATFORM_ACCESS_FORBIDDEN", status_code=403)

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)


# ============================================================================
# 5. PLATFORM ROLE SERVICE
# ============================================================================

@register_service("platform_role")
class PlatformRoleService(BaseService):
    def check_permission(self, context):
        is_root = getattr(context, "is_root_admin", False) or getattr(getattr(context, "user", None), "is_root_admin", False)
        if is_root:
            return True
        user = getattr(context, "user", None)
        if getattr(user, "plane", "client") == "platform":
            if context.action in ("read", "report", "statistics"):
                return True
        raise AuthorizationError("Platform Role management requires Root Admin privileges.", code="ROOT_ADMIN_REQUIRED", status_code=403)

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)


# ============================================================================
# 6. PLATFORM USER SERVICE
# ============================================================================

@register_service("platform_user")
class PlatformUserService(BaseService):
    def check_permission(self, context):
        is_root = getattr(context, "is_root_admin", False) or getattr(getattr(context, "user", None), "is_root_admin", False)
        if is_root:
            return True
        user = getattr(context, "user", None)
        if getattr(user, "plane", "client") == "platform":
            if context.action in ("read", "report", "statistics"):
                return True
        raise AuthorizationError("Platform User management requires Root Admin privileges.", code="ROOT_ADMIN_REQUIRED", status_code=403)

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)

    def get_forbidden_fields(self, context):
        return ["password"]

    def before_create(self, context, data):
        from django.contrib.auth.hashers import make_password
        if data.get("password"):
            data["password"] = make_password(data["password"])
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        from django.contrib.auth.hashers import make_password
        if "password" in data and data["password"]:
            data["password"] = make_password(data["password"])
        return data


# ============================================================================
# 7. RETENTION POLICY SERVICE
# ============================================================================

@register_service("retention_policy")
class RetentionPolicyService(BaseService):
    def check_permission(self, context):
        is_root = getattr(context, "is_root_admin", False) or getattr(getattr(context, "user", None), "is_root_admin", False)
        if is_root:
            return True
        user = getattr(context, "user", None)
        if getattr(user, "plane", "client") == "platform":
            if context.action in ("read", "report", "statistics"):
                return True
            raise AuthorizationError("Management Viewer has read-only access to retention policies.", code="READ_ONLY_ROLE", status_code=403)
        raise AuthorizationError("Access to retention policies is restricted to Platform Operators.", code="PLATFORM_ACCESS_FORBIDDEN", status_code=403)

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)


# ============================================================================
# 8. RETENTION EVENT SERVICE
# ============================================================================

@register_service("retention_event")
class RetentionEventService(BaseService):
    def check_permission(self, context):
        is_root = getattr(context, "is_root_admin", False) or getattr(getattr(context, "user", None), "is_root_admin", False)
        if is_root:
            return True
        user = getattr(context, "user", None)
        if getattr(user, "plane", "client") == "platform":
            if context.action in ("read", "report", "statistics"):
                return True
            raise AuthorizationError("Management Viewer has read-only access to retention events.", code="READ_ONLY_ROLE", status_code=403)
        raise AuthorizationError("Access to retention events is restricted to Platform Operators.", code="PLATFORM_ACCESS_FORBIDDEN", status_code=403)

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)

    def before_update(self, context, instance, data):
        action_cmd = data.get("action_cmd") or data.get("action")
        if action_cmd == "PURGE_NOW":
            from .retention_worker import StorageRetentionWorker
            result = StorageRetentionWorker.execute_purge_event(instance)
            data["status"] = "Purged"
            data["purged_at"] = timezone.now()
            data["reclaimed_bytes"] = result.get("reclaimed_bytes", 0)
            data["reclaimed_files_count"] = result.get("reclaimed_files_count", 0)
            data["reclaimed_db_rows_count"] = result.get("reclaimed_db_rows_count", 0)
            data["initiated_by"] = "Root_Admin_Manual"

        elif action_cmd == "EXTEND_GRACE":
            import datetime
            days_to_add = int(data.get("extend_days", 30))
            data["purge_scheduled_at"] = instance.purge_scheduled_at + datetime.timedelta(days=days_to_add)

        elif action_cmd == "RESTORE":
            data["status"] = "Cancelled"

        return data



