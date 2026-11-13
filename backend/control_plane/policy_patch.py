"""
PolicyEngine Two-Plane & Modular Entitlement Enforcement Patch
=============================================================
Single source of truth for platform vs. client plane decoupling:
1. Platform Plane:
   - Platform Root Admin (is_root_admin=True) has full bypass on platform models.
   - Platform Management Viewer has read-only access; mutations raise 403 READ_ONLY_ROLE.
   - Client users attempting to access platform models (tenant, provisioning_run, platform_user, etc.)
     are strictly rejected with 403 PLATFORM_ACCESS_FORBIDDEN.
   - Public & Client Catalog Read: Read actions on 'module' are open to public / clients via Populate.
     Mutations (create, update, delete on 'module') remain strictly locked to Platform Root Admin.
2. Client Plane:
   - Core models (user, role, department, etc.) are accessible to active tenants.
   - Business modules (attendance, payroll, crm, billing, etc.) are strictly gated by tenant.enabled_modules.
   - Subscribed modules: Client SuperAdmin has bypass within purchased modules; other users evaluate policies.
   - Unsubscribed modules: Rejected with 403 MODULE_NOT_SUBSCRIBED for all tenant users.
"""

from typing import Any
from django.db.models import Q
from populate_core.policy.engine import PolicyEngine
from populate_core.response.exceptions import AuthorizationError
from populate_core.registry.model_registry import ModelRegistry
from control_plane.registry import (
    is_platform_model,
    is_core_model,
    get_module_for_model,
    is_model_entitled,
)

_original_authorize = PolicyEngine.authorize


@classmethod
def decoupled_authorize(cls, context: Any) -> Any:
    model_clean = (context.model_name or "").lower().strip()
    canonical_model = ModelRegistry._aliases.get(model_clean, model_clean)
    user = getattr(context, "user", None)
    is_root = getattr(context, "is_root_admin", False) or getattr(user, "is_root_admin", False)
    user_plane = getattr(user, "plane", "client")

    # =========================================================================
    # 1. PLATFORM CONTROL PLANE
    # =========================================================================
    if is_platform_model(canonical_model):
        # A. Public & Client Catalog Read exception for 'module'
        if canonical_model in ("module", "modules") and context.action in ("read", "report", "statistics", "aggregate"):
            if is_root or getattr(getattr(user, "role", None), "role_id", "") in ("root_admin", "superadmin"):
                context.metadata["policy_q"] = Q()
                context.metadata["forbidden_fields"] = []
                context.metadata["allowed_fields"] = None
                context.metadata["authorized_by"] = "root_admin"
                return context
            # Fall through to service/public read handling
            return _original_authorize(context)

        # B. Platform Root Admin Full Bypass
        if is_root or (user_plane == "platform" and getattr(getattr(user, "role", None), "is_root_admin", False)):
            context.metadata["policy_q"] = Q()
            context.metadata["forbidden_fields"] = []
            context.metadata["allowed_fields"] = None
            context.metadata["authorized_by"] = "root_admin"
            return context

        # C. Platform Staff (e.g. Management Viewer)
        if user_plane == "platform":
            role_id = getattr(getattr(user, "role", None), "role_id", "")
            if role_id == "management_viewer":
                if context.action in ("read", "report", "statistics", "aggregate"):
                    context.metadata["policy_q"] = Q()
                    context.metadata["forbidden_fields"] = []
                    context.metadata["allowed_fields"] = None
                    context.metadata["authorized_by"] = "management_viewer_read"
                    return context
                raise AuthorizationError(
                    "Management Viewer has read-only access to control plane resources.",
                    code="READ_ONLY_ROLE",
                    status_code=403,
                )

        # D. Client users or anonymous attempting to access other platform models
        raise AuthorizationError(
            "Access to Control Plane models is restricted to Platform Operators.",
            code="PLATFORM_ACCESS_FORBIDDEN",
            status_code=403,
        )

    # =========================================================================
    # 2. CLIENT PLANE
    # =========================================================================
    if user and getattr(user, "is_authenticated", False) and user_plane == "client":
        # Core Models: Universal access for active tenants
        if is_core_model(canonical_model):
            if context.is_superadmin:
                context.metadata["policy_q"] = Q()
                context.metadata["forbidden_fields"] = []
                context.metadata["allowed_fields"] = None
                context.metadata["authorized_by"] = "client_superadmin_core"
                return context
            return _original_authorize(context)

        # Business Modules (Attendance, Payroll, CRM, Billing, etc.)
        tenant_id = (
            getattr(context, "tenant_id", None)
            or getattr(user, "tenant_id", None)
            or getattr(getattr(user, "tenant", None), "tenant_id", None)
        )
        enabled_modules = []
        if getattr(context, "tenant_context", None):
            enabled_modules = context.tenant_context.get("enabled_modules", [])
        if not enabled_modules and tenant_id:
            from control_plane.models import Tenant
            tenant_obj = Tenant.objects.filter(tenant_id=tenant_id).first()
            if tenant_obj:
                enabled_modules = tenant_obj.enabled_modules or []

        # Modular Entitlement Gate
        if not is_model_entitled(canonical_model, enabled_modules):
            module_name = get_module_for_model(canonical_model) or "unknown"
            raise AuthorizationError(
                f"Organization has not subscribed to module '{module_name}'.",
                code="MODULE_NOT_SUBSCRIBED",
                status_code=403,
                details={"model": canonical_model, "module": module_name},
            )

        # Subscribed Module: SuperAdmin bypass within purchased module
        if context.is_superadmin:
            context.metadata["policy_q"] = Q()
            context.metadata["forbidden_fields"] = []
            context.metadata["allowed_fields"] = None
            context.metadata["authorized_by"] = "client_superadmin_module"
            return context

    return _original_authorize(context)


def apply_policy_patch() -> None:
    """Hooks the decoupled Two-Plane and Modular Entitlements gate into PolicyEngine."""
    PolicyEngine.authorize = decoupled_authorize
