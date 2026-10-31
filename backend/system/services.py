from decimal import Decimal
import logging
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from populate_core.registry import BaseService, register_service
from populate_core.response.exceptions import AuthorizationError, ValidationError, NotFoundError

logger = logging.getLogger("system.services")


# ============================================================================
# 1. STATUS CONFIG SERVICE
# ============================================================================

@register_service("status_config")
class StatusConfigService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True
        return None

    def get_policy_scope(self, context):
        return Q(status=1)


# ============================================================================
# 2. STATUS MAPPING SERVICE
# ============================================================================

@register_service("status_mapping")
class StatusMappingService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True
        return None

    def get_policy_scope(self, context):
        return Q(is_active=True)


# ============================================================================
# 3. EMAIL CONFIG SERVICE
# ============================================================================

@register_service("email_config")
class EmailConfigService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_forbidden_fields(self, context):
        # Never project outbound SMTP password in any API read response
        return ["password"]

    def before_create(self, context, data):
        if not data.get("host"):
            raise ValueError("host is required for email config.")
        if not data.get("from_email"):
            raise ValueError("from_email is required for email config.")

        if "password" in data:
            data["password"] = str(data["password"]).strip()
        data["status"] = 1
        return data

    def before_update(self, context, instance, data):
        if "password" in data:
            data["password"] = str(data["password"]).strip()
        return data


# ============================================================================
# 4. SERVICE PROVIDER SERVICE
# ============================================================================

@register_service("service_provider")
class ServiceProviderService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True
        return None

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1, status="Active")

    def before_create(self, context, data):
        if not data.get("name"):
            raise ValueError("name is required for service provider.")
        data["status"] = data.get("status", "Active")
        data["lifecycle_status"] = 1
        return data


# ============================================================================
# 5. RELEASE NOTE SERVICE
# ============================================================================

@register_service("release_note")
class ReleaseNoteService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        # Public and internal users can view published release notes
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True

        # Allow authenticated users to mark release note as seen
        if context.action == "update" and getattr(context.user, "is_authenticated", False):
            if "mark_seen" in getattr(context, "body", {}):
                return True

        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()
        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "release_note.manage") or PolicyEngine.has_capability(context, "release_note.all"):
            return Q(lifecycle_status=1)
        return Q(lifecycle_status=1, is_published=True)

    def before_create(self, context, data):
        from .models import ReleaseNote

        if not data.get("version"):
            raise ValueError("version is required for release note.")
        if not data.get("title"):
            raise ValueError("title is required for release note.")

        # If marked is_latest, clear is_latest from all previous notes
        if data.get("is_latest") is True:
            ReleaseNote.objects.filter(is_latest=True).update(is_latest=False)

        data["created_by_id"] = getattr(context.user, "id", None)
        data["meta_status"] = "active"
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        from .models import ReleaseNote

        if data.get("is_latest") is True and not instance.is_latest:
            ReleaseNote.objects.filter(is_latest=True).exclude(id=instance.id).update(is_latest=False)

        # Mark release note seen by current user
        mark_seen = data.pop("mark_seen", None)
        if mark_seen and getattr(context.user, "is_authenticated", False):
            seen_entries = list(instance.seen_by or [])
            if not any(s.get("employeeId") == context.user.id for s in seen_entries):
                seen_entries.append({
                    "employeeId": context.user.id,
                    "viewedAt": timezone.now().isoformat()
                })
            data["seen_by"] = seen_entries

        return data


# ============================================================================
# 6. RESOURCE SERVICE (CANONICAL CATALOG)
# ============================================================================

@register_service("resource")
class ResourceService(BaseService):
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
        if not data.get("key"):
            raise ValueError("key is required for resource catalog.")
        if not data.get("display_name"):
            raise ValueError("display_name is required for resource catalog.")
        data["key"] = str(data["key"]).strip().lower()
        data["is_active"] = data.get("is_active", True)
        data["lifecycle_status"] = 1
        return data


# ============================================================================
# 7. WORKFLOW SERVICE (MULTI-STEP APPROVAL ENGINE)
# ============================================================================

@register_service("workflow")
class WorkflowService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)

    def before_create(self, context, data):
        if not data.get("name"):
            raise ValueError("name is required for workflow.")
        if not data.get("model_name"):
            raise ValueError("model_name is required for workflow.")
        if not data.get("trigger_type"):
            raise ValueError("trigger_type is required for workflow.")

        data["created_by_id"] = getattr(context.user, "id", None)
        data["is_active"] = data.get("is_active", True)
        data["lifecycle_status"] = 1
        return data


# ============================================================================
# 8. PRODUCT SERVICE (PRODUCT CATALOG)
# ============================================================================

@register_service("product")
class ProductService(BaseService):
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
        if not data.get("name"):
            raise ValueError("name is required for product.")
        if not data.get("code"):
            raise ValueError("code is required for product.")

        data["code"] = str(data["code"]).strip().upper()
        data["is_active"] = data.get("is_active", True)
        data["lifecycle_status"] = 1
        return data

