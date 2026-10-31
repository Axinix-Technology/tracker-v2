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
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            # Allow public subdomain/tenant lookup
            if context.action in ("read", "report", "statistics", "aggregate"):
                return True
            return False
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True
        # Creating or modifying tenants requires superadmin
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
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
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return Q(is_active=True, lifecycle_status=1)


# ============================================================================
# 3. MODULE SERVICE (GLOBAL ENTITLEMENTS)
# ============================================================================

@register_service("module")
class ModuleService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True
        return None

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
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)

