import logging
from django.db.models import Q
from django.utils import timezone
from populate_core.registry import BaseService, register_service

logger = logging.getLogger(__name__)


# ============================================================================
# 1. NOTIFICATION SERVICE
# ============================================================================

@register_service("notification")
class NotificationService(BaseService):
    def check_permission(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return True

        if getattr(context.user, "is_authenticated", False):
            return True

        return None

    def get_policy_scope(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return Q()
        return Q(recipient=context.user)

    def before_read(self, context, queryset):
        queryset = super().before_read(context, queryset)
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super and getattr(context.user, "is_authenticated", False):
            queryset = queryset.filter(recipient=context.user)
        return queryset

    def before_create(self, context, data):
        # Prevent sender spoofing: strictly stamp authenticated user as sender
        if hasattr(context, "user") and getattr(context.user, "is_authenticated", False):
            data["sender_id"] = context.user.id

        recipient_id = data.get("recipient") or data.get("recipient_id")
        if not recipient_id:
            raise ValueError("Notification requires a valid recipient.")

        if "isRead" in data:
            data["is_read"] = data.pop("isRead")

        data["status"] = data.get("status", 1)
        return data

    def before_update(self, context, instance, data):
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super and getattr(context.user, "is_authenticated", False):
            # Enforce that users can only mark their own notifications as read
            if instance.recipient != context.user:
                raise PermissionError("You do not have permission to modify another user's notifications.")

        if "isRead" in data:
            data["is_read"] = data.pop("isRead")

        return data


# ============================================================================
# 2. NOTIFICATION RECEPTIONIST SERVICE
# ============================================================================

@register_service("notification_receptionist")
class NotificationReceptionistService(BaseService):
    def check_permission(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return True

        if getattr(context.user, "is_authenticated", False):
            return True

        return None

    def get_policy_scope(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return Q()
        return Q(receiver=context.user)

    def before_read(self, context, queryset):
        queryset = super().before_read(context, queryset)
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super and getattr(context.user, "is_authenticated", False):
            queryset = queryset.filter(receiver=context.user)
        return queryset

    def before_update(self, context, instance, data):
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super and getattr(context.user, "is_authenticated", False):
            if instance.receiver != context.user:
                raise PermissionError("You do not have permission to modify another user's receptionist record.")

        if "isRead" in data:
            data["is_read"] = data.pop("isRead")

        if data.get("is_read") is True and not instance.read_at:
            data["read_at"] = timezone.now()

        return data


# ============================================================================
# 3. NOTIFICATION RULE SERVICE
# ============================================================================

@register_service("notification_rule")
class NotificationRuleService(BaseService):
    def check_permission(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return True
        # Notification rules are platform-wide configuration
        if getattr(context.user, "is_staff", False):
            return True
        return None

    def before_create(self, context, data):
        if hasattr(context, "user") and getattr(context.user, "is_authenticated", False):
            data["created_by_id"] = context.user.id
            data["updated_by_id"] = context.user.id
        return data

    def before_update(self, context, instance, data):
        if hasattr(context, "user") and getattr(context.user, "is_authenticated", False):
            data["updated_by_id"] = context.user.id
        return data


# ============================================================================
# 4. NOTIFICATION PREFERENCE SERVICE
# ============================================================================

@register_service("notification_preference")
class NotificationPreferenceService(BaseService):
    def check_permission(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return True
        if getattr(context.user, "is_authenticated", False):
            return True
        return None

    def get_policy_scope(self, context):
        is_super = getattr(context.user, "is_superadmin", False)
        if is_super:
            return Q()
        return Q(employee=context.user)

    def before_read(self, context, queryset):
        queryset = super().before_read(context, queryset)
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super and getattr(context.user, "is_authenticated", False):
            queryset = queryset.filter(employee=context.user)
        return queryset

    def before_create(self, context, data):
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super and getattr(context.user, "is_authenticated", False):
            data["employee_id"] = context.user.id
        return data

    def before_update(self, context, instance, data):
        is_super = getattr(context.user, "is_superadmin", False)
        if not is_super and getattr(context.user, "is_authenticated", False):
            if instance.employee_id != context.user.id:
                raise PermissionError("You can only modify your own notification preferences.")
        return data
