import datetime
from django.db import models
from django.utils import timezone
from populate_core.registry import BaseService, register_service


# ============================================================================
# 1. CONTRIBUTION CATEGORY SERVICE
# ============================================================================

@register_service("contribution_category")
class ContributionCategoryService(BaseService):
    def check_permission(self, context):
        if context.action in ("read", "aggregate", "report") and getattr(context.user, "is_authenticated", False):
            return True
        if getattr(context.user, "is_superadmin", False):
            return True
        return None

    def before_create(self, context, data):
        if not data.get("name"):
            raise ValueError("Category name is required.")
        data["is_active"] = data.get("is_active", True)
        return data


# ============================================================================
# 2. CONTRIBUTION FACTOR SERVICE
# ============================================================================

@register_service("contribution_factor")
class ContributionFactorService(BaseService):
    def check_permission(self, context):
        if context.action in ("read", "aggregate") and getattr(context.user, "is_authenticated", False):
            return True
        if getattr(context.user, "is_superadmin", False):
            return True
        return None


# ============================================================================
# 3. WORK CONTRIBUTION SERVICE (POINTS CALCULATION & LIFECYCLE HOOKS)
# ============================================================================

@register_service("work_contribution")
class WorkContributionService(BaseService):
    FACTOR_WEIGHTS = {
        "factor_effort": 20.0,
        "factor_complexity": 15.0,
        "factor_deliverable": 25.0,
        "factor_quality": 20.0,
        "factor_evidence": 10.0,
        "factor_outcome": 10.0,
    }

    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        # All authenticated team members can read contributions for the company dashboard & reports
        if context.action in ("read", "create", "report", "statistics", "aggregate"):
            return True

        # Defer updates and deletions to ABAC PolicyEngine
        return None

    def get_policy_scope(self, context):
        # Platform-wide transparency: Team members can see all active contributions
        # to ensure fair, open equity and profit share calculations
        return models.Q(lifecycle_status=1)

    def _calculate_points(self, data, existing_instance=None):
        """
        Pure, deterministic mathematical calculation for factor % and final points.
        Cannot be spoofed or bypassed by client payloads.
        """
        worked_days = float(data.get("worked_days", getattr(existing_instance, "worked_days", 1.0) if existing_instance else 1.0))
        base_points = float(data.get("base_points", getattr(existing_instance, "base_points", 10.0) if existing_instance else 10.0))

        factor_sum = 0.0
        for factor_field, weight in self.FACTOR_WEIGHTS.items():
            val = data.get(factor_field, getattr(existing_instance, factor_field, True) if existing_instance else True)
            if val is True or str(val).lower() in ("true", "1", "yes"):
                factor_sum += weight

        factor_percentage = round(factor_sum, 2)
        final_points = round((worked_days * base_points) * (factor_percentage / 100.0), 2)

        data["factor_percentage"] = factor_percentage
        data["final_points"] = final_points
        data["worked_days"] = worked_days
        data["base_points"] = base_points

        # Auto-detect Delivery Status based on Deliverable & Completion factor
        is_deliverable = data.get("factor_deliverable", getattr(existing_instance, "factor_deliverable", True) if existing_instance else True)
        is_deliverable_bool = is_deliverable is True or str(is_deliverable).lower() in ("true", "1", "yes")

        if not is_deliverable_bool and not data.get("delivery_status"):
            data["delivery_status"] = "in_progress"
        elif is_deliverable_bool and data.get("delivery_status") in (None, "in_progress"):
            data["delivery_status"] = "completed"

        return data

    def before_create(self, context, data):
        target_user = data.get("user") or data.get("user_id")

        from populate_core.policy.engine import PolicyEngine
        has_manage = context.is_superadmin or PolicyEngine.has_capability(context, "work_contribution.create")

        if not has_manage or not target_user:
            data["user_id"] = context.user.id
        else:
            data["user_id"] = target_user if not hasattr(target_user, "id") else target_user.id

        if not data.get("activity"):
            raise ValueError("Work description (activity) is required.")

        data["date"] = data.get("date") or timezone.now().date()
        data["scope"] = data.get("scope", "Company Contribution")
        data["project_name"] = data.get("project_name", "Axinix Technologies")
        data["lifecycle_status"] = 1
        data["approval_status"] = data.get("approval_status", "approved" if context.is_superadmin else "submitted")

        # Execute pure deterministic points calculation
        data = self._calculate_points(data)
        return data

    def before_update(self, context, instance, data):
        data = self._calculate_points(data, existing_instance=instance)
        return data

