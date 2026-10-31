from decimal import Decimal
import logging
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from populate_core.registry import BaseService, register_service
from populate_core.response.exceptions import AuthorizationError, ValidationError, NotFoundError

logger = logging.getLogger("crm.services")


# ============================================================================
# 1. LEAD TYPE SERVICE (MASTER)
# ============================================================================

@register_service("lead_type")
class LeadTypeService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True
        return None

    def get_policy_scope(self, context):
        return Q(status="Active")


# ============================================================================
# 2. REFERENCE TYPE SERVICE (MASTER)
# ============================================================================

@register_service("reference_type")
class ReferenceTypeService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True
        return None

    def get_policy_scope(self, context):
        return Q(status="Active")


# ============================================================================
# 3. CONTACT SERVICE (LEAD MANAGEMENT)
# ============================================================================

@register_service("contact")
class ContactService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()
        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "contact.read") or PolicyEngine.has_capability(context, "contact.all"):
            return Q(lifecycle_status=1)
        # Sales representatives see leads assigned to them or contacted by them
        return Q(lifecycle_status=1) & (Q(assigned_to=context.user) | Q(contacted_by=context.user))

    def before_create(self, context, data):
        if not data.get("first_name"):
            raise ValueError("first_name is required for contact.")

        data["status"] = data.get("status", "New")
        data["meta_status"] = "active"
        data["lifecycle_status"] = 1

        if not data.get("assigned_to") and not data.get("assigned_to_id"):
            data["assigned_to_id"] = getattr(context.user, "id", None)

        return data

    def before_update(self, context, instance, data):
        new_log = data.pop("new_contact_log", None)
        now = timezone.now()

        # Append structured contact history log
        if new_log and isinstance(new_log, dict):
            history = list(instance.contact_history or [])
            history.append({
                "contactedBy": getattr(context.user, "id", None),
                "contactedAt": now.isoformat(),
                "method": new_log.get("method", "Call"),
                "notes": new_log.get("notes", ""),
                "outcome": new_log.get("outcome", "Follow Up")
            })
            data["contact_history"] = history
            data["contacted_by_id"] = getattr(context.user, "id", None)
            data["contacted_at"] = now

            if instance.status == "New" and "status" not in data:
                data["status"] = "Contacted"

        # Conversion to Client
        new_status = data.get("status")
        if new_status == "Converted" and instance.status != "Converted":
            from users.models import Client
            if not instance.converted_client and not data.get("converted_client_id"):
                company_name = instance.company_name or f"{instance.first_name} {instance.last_name or ''}".strip()
                client, _ = Client.objects.get_or_create(
                    name=company_name,
                    defaults={
                        "email": instance.email or "",
                        "phone": instance.phone or "",
                        "status": 1
                    }
                )
                data["converted_client_id"] = client.id

        return data


# ============================================================================
# 4. OPPORTUNITY SERVICE (SALES DEAL PIPELINE)
# ============================================================================

@register_service("opportunity")
class OpportunityService(BaseService):
    STAGE_PROBABILITIES = {
        "New": 10,
        "Discovery": 20,
        "Proposal": 50,
        "Negotiation": 80,
        "Won": 100,
        "Lost": 0
    }

    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()
        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "opportunity.read") or PolicyEngine.has_capability(context, "opportunity.all"):
            return Q(lifecycle_status=1)
        return Q(lifecycle_status=1) & Q(owner=context.user)

    def before_create(self, context, data):
        if not data.get("name"):
            raise ValueError("Opportunity name is required.")

        account_id = data.get("account") or data.get("account_id") or data.get("accountId")
        if not account_id:
            raise ValueError("account is required for opportunity.")
        data["account_id"] = account_id if not hasattr(account_id, "id") else account_id.id

        owner_id = data.get("owner") or data.get("owner_id") or data.get("ownerId")
        data["owner_id"] = (owner_id if not hasattr(owner_id, "id") else owner_id.id) or getattr(context.user, "id", None)

        stage = data.get("stage", "New")
        data["stage"] = stage
        data["probability"] = data.get("probability") or self.STAGE_PROBABILITIES.get(stage, 10)
        data["created_by_id"] = getattr(context.user, "id", None)
        data["meta_status"] = "active"
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_stage = data.get("stage")
        now = timezone.now()

        if new_stage and new_stage != instance.stage:
            if new_stage not in self.STAGE_PROBABILITIES:
                raise ValueError(f"Invalid opportunity stage '{new_stage}'.")

            if "probability" not in data:
                data["probability"] = self.STAGE_PROBABILITIES[new_stage]

            if new_stage == "Won":
                data["actual_close_date"] = now.date()
                data["probability"] = 100
            elif new_stage == "Lost":
                data["actual_close_date"] = now.date()
                data["probability"] = 0
                if not data.get("lost_reason") and not instance.lost_reason:
                    raise ValueError("lost_reason is required when marking opportunity as Lost.")

        return data


# ============================================================================
# 5. CRM ACTIVITY SERVICE (INTERACTION LOG)
# ============================================================================

@register_service("crm_activity")
class CRMActivityService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)

    def before_create(self, context, data):
        client_id = data.get("client") or data.get("client_id") or data.get("clientId")
        if not client_id:
            raise ValueError("client is required for CRM activity.")
        data["client_id"] = client_id if not hasattr(client_id, "id") else client_id.id

        if not data.get("content"):
            raise ValueError("content is required for CRM activity.")

        data["performed_by_id"] = getattr(context.user, "id", None)
        data["timestamp"] = timezone.now()
        data["type"] = data.get("type", "Note")
        data["lifecycle_status"] = 1
        return data


# ============================================================================
# 6. CRM MEETING SERVICE (CALENDAR SCHEDULING)
# ============================================================================

@register_service("crm_meeting")
class CRMMeetingService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)

    def before_create(self, context, data):
        client_id = data.get("client") or data.get("client_id") or data.get("clientId")
        if not client_id:
            raise ValueError("client is required for CRM meeting.")
        data["client_id"] = client_id if not hasattr(client_id, "id") else client_id.id

        if not data.get("title"):
            raise ValueError("Meeting title is required.")

        sched = data.get("scheduled_time") or data.get("scheduledTime")
        end = data.get("end_time") or data.get("endTime")
        if not sched or not end:
            raise ValueError("scheduled_time and end_time are required.")

        if str(end) <= str(sched):
            raise ValueError("end_time must be strictly after scheduled_time.")

        data["scheduled_time"] = sched
        data["end_time"] = end
        data["created_by_id"] = getattr(context.user, "id", None)
        data["status"] = data.get("status", "Scheduled")
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_status = data.get("status")
        now = timezone.now()

        if new_status and new_status != instance.status:
            if new_status == "Started":
                data["actual_start_time"] = now
            elif new_status == "Completed":
                data["actual_end_time"] = now

        return data

