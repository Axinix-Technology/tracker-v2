"""
Control Plane & Enterprise SaaS Entitlement Registry
=====================================================
Single source of truth defining Plane Boundaries and Module Entitlements:
1. PLATFORM PLANE: Control Plane operations (PlatformUser, PlatformRole, Tenants, Modules)
2. CLIENT CORE: Foundational models always accessible to any active tenant
3. CLIENT BUSINESS MODULES: Licensed ERP suites gated by tenant.enabled_modules
"""

from typing import Dict, List, Set, Optional

# ============================================================================
# 1. PLATFORM CONTROL PLANE MODELS (ROOT / PLATFORM STAFF ONLY)
# ============================================================================

PLATFORM_MODELS: Set[str] = {
    "tenant",
    "module",
    "user_login",
    "provisioning_run",
    "platform_user",
    "platform_role",
    "retention_policy",
    "retention_event",
    "audit_log",
}

# ============================================================================
# 2. CLIENT CORE FOUNDATION MODELS (UNIVERSALLY ACCESSIBLE TO ACTIVE TENANTS)
# ============================================================================

CLIENT_CORE_MODELS: Set[str] = {
    "user",
    "role",
    "department",
    "designation",
    "company",
    "client",
    "project_type",
    "notification",
    "notification_preference",
    "notification_receptionist",
    "notification_rule",
    "dashboard_schema",
    "dashboard_widget",
    "status_config",
    "status_mapping",
    "release_note",
    "general_settings",
    "resource",
    "workflow",
    "service_provider",
    "product",
}

# ============================================================================
# 3. CLIENT BUSINESS MODULE TO MODEL MAPPING
# ============================================================================

CLIENT_BUSINESS_MODULES: Dict[str, Set[str]] = {
    "attendance": {
        "attendance",
        "attendance_policy",
        "holiday",
        "holiday_override",
        "leave",
        "leave_policy",
        "leave_transaction",
        "leave_type",
        "permission_balance",
        "permission_transaction",
        "regularization",
        "shift",
        "shift_assignment",
        "wfh_request",
        "comp_off_request",
    },
    "payroll": {
        "salary_structure",
        "payroll_run",
        "payroll",
        "expense",
    },
    "crm": {
        "opportunity",
        "contact",
        "lead_type",
        "reference_type",
        "crm_activity",
        "crm_meeting",
    },
    "billing": {
        "quotation",
        "quotation_revision",
        "order_acknowledgement",
        "invoice",
        "payment",
        "payment_journal",
        "client_ledger",
        "period_closure",
    },
    "tasks": {
        "task",
        "task_board",
        "sprint",
        "task_type",
        "daily_activity",
        "employee_task_queue",
        "employee_task_queue_request",
        "time_tracker_session",
        "todo",
        "milestone",
    },
    "tickets": {
        "ticket",
        "ticket_activity_log",
        "ticket_attachment",
        "ticket_comment",
        "ticket_participant",
        "ticket_status_history",
    },
    "assets": {
        "asset",
        "asset_category",
        "asset_allocation",
        "asset_assignment",
        "asset_incident",
        "asset_invoice",
        "asset_payment",
        "asset_purchase",
        "asset_repair",
        "asset_stock_ledger",
        "asset_vendor",
    },
    "recruitment": {
        "candidate",
        "job_opening",
        "job_category",
        "job_type",
        "onboarding",
        "onboarding_template",
    },
    "hr": {
        "employee_document",
        "employee_lifecycle_history",
        "hr_policy",
        "user_override",
    },
    "feed": {
        "feed_post",
        "feed_comment",
        "feed_group",
        "feed_channel",
        "team_message",
        "comments_thread",
    },
}


# ============================================================================
# 4. RESOLUTION HELPERS
# ============================================================================

def is_platform_model(model_name: str) -> bool:
    clean = (model_name or "").lower().strip()
    return clean in PLATFORM_MODELS


def is_core_model(model_name: str) -> bool:
    clean = (model_name or "").lower().strip()
    return clean in CLIENT_CORE_MODELS


def get_module_for_model(model_name: str) -> Optional[str]:
    clean = (model_name or "").lower().strip()
    if is_platform_model(clean):
        return "control_plane"
    if is_core_model(clean):
        return "core"
    for module_key, models in CLIENT_BUSINESS_MODULES.items():
        if clean in models:
            return module_key
    return None


def is_model_entitled(model_name: str, enabled_modules: List[str]) -> bool:
    """
    Checks if an organization's enabled_modules contains the module for model_name.
    Core models are unconditionally entitled.
    """
    clean = (model_name or "").lower().strip()
    if is_core_model(clean):
        return True
    mod = get_module_for_model(clean)
    if not mod:
        # Unknown/unmapped model: fail closed
        return False
    return mod in enabled_modules

