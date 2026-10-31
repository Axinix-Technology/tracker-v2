from decimal import Decimal
import logging
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from populate_core.registry import BaseService, register_service
from populate_core.response.exceptions import AuthorizationError, ValidationError, NotFoundError

logger = logging.getLogger("recruitment.services")


# ============================================================================
# 1. JOB CATEGORY SERVICE (MASTER)
# ============================================================================

@register_service("job_category")
class JobCategoryService(BaseService):
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
# 2. JOB TYPE SERVICE (MASTER)
# ============================================================================

@register_service("job_type")
class JobTypeService(BaseService):
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
# 3. JOB OPENING SERVICE (VACANCY POSTINGS)
# ============================================================================

@register_service("job_opening")
class JobOpeningService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        # Public job board read access
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            if context.action in ("read", "report", "statistics", "aggregate"):
                return True
            return False

        # Authenticated employees can read internal postings
        if context.action in ("read", "report", "statistics", "aggregate"):
            return True

        # Defer authoring/management to PolicyEngine (HR AccessPolicy)
        return None

    def get_policy_scope(self, context):
        is_authenticated = bool(getattr(context, "user", None) and getattr(context.user, "is_authenticated", False))
        if context.is_superadmin:
            return Q()

        from populate_core.policy.engine import PolicyEngine
        if is_authenticated and (PolicyEngine.has_capability(context, "job_opening.read") or PolicyEngine.has_capability(context, "job_opening.all")):
            return Q(lifecycle_status=1)

        # Public visitors and employees without HR capability only see Published vacancies
        return Q(lifecycle_status=1, status="Published")

    def before_create(self, context, data):
        if not data.get("title"):
            raise ValueError("title is required for job opening.")

        data["status"] = data.get("status", "Draft")
        data["filled"] = 0
        data["openings"] = int(data.get("openings") or 1)
        data["created_by_id"] = getattr(context.user, "id", None)
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_status = data.get("status")
        now = timezone.now()

        if new_status and new_status != instance.status:
            if new_status == "Published":
                data["published_at"] = now
            elif new_status in ("Closed", "Filled"):
                data["closed_at"] = now

        return data


# ============================================================================
# 4. CANDIDATE SERVICE (APPLICANT TRACKING)
# ============================================================================

@register_service("candidate")
class CandidateService(BaseService):
    STAGE_ORDER = [
        "Applied", "Screening", "Interview", "Offered", "Hired", "Rejected", "Withdrawn"
    ]

    def check_permission(self, context):
        if context.is_superadmin:
            return True

        # Allow external candidate applications (Careers Portal public apply)
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            if context.action == "create":
                return True
            return False

        # Defer candidate evaluation/pipeline stages to PolicyEngine
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()
        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "candidate.read") or PolicyEngine.has_capability(context, "candidate.all"):
            return Q(lifecycle_status=1)
        return Q(lifecycle_status=1)

    def before_create(self, context, data):
        from .models import Candidate

        if not data.get("first_name"):
            raise ValueError("first_name is required for candidate.")
        if not data.get("email"):
            raise ValueError("email is required for candidate.")

        job_id = data.get("job_opening") or data.get("job_opening_id") or data.get("jobOpeningId")
        if not job_id:
            raise ValueError("job_opening is required for candidate.")
        data["job_opening_id"] = job_id if not hasattr(job_id, "id") else job_id.id

        now = timezone.now()
        year = now.year

        # Sequential Application ID: APP-YYYY-XXXX
        if not data.get("application_id"):
            last_app = Candidate.objects.filter(application_id__startswith=f"APP-{year}-").order_by("-id").first()
            if last_app and last_app.application_id:
                try:
                    last_seq = int(last_app.application_id.split("-")[-1])
                    next_seq = last_seq + 1
                except Exception:
                    next_seq = Candidate.objects.count() + 1
            else:
                next_seq = 1

            gen_id = f"APP-{year}-{next_seq:04d}"
            while Candidate.objects.filter(application_id=gen_id).exists():
                next_seq += 1
                gen_id = f"APP-{year}-{next_seq:04d}"
            data["application_id"] = gen_id

        data["stage"] = data.get("stage", "Applied")
        data["created_by_id"] = getattr(context.user, "id", None) if getattr(context, "user", None) else None
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_stage = data.get("stage")
        now = timezone.now()

        if new_stage and new_stage != instance.stage:
            history = list(instance.stage_history or [])
            history.append({
                "stage": new_stage,
                "movedAt": now.isoformat(),
                "movedBy": getattr(context.user, "id", None),
                "note": data.get("stage_note") or ""
            })
            data["stage_history"] = history

            # When Hired, increment JobOpening filled count
            if new_stage == "Hired" and instance.stage != "Hired":
                job = instance.job_opening
                job.filled += 1
                if job.filled >= job.openings:
                    job.status = "Filled"
                    job.closed_at = now
                job.save(update_fields=["filled", "status", "closed_at", "updated_at"])

        return data


# ============================================================================
# 5. ONBOARDING TEMPLATE SERVICE
# ============================================================================

@register_service("onboarding_template")
class OnboardingTemplateService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1, is_active=True)

    def before_create(self, context, data):
        if not data.get("title"):
            raise ValueError("title is required for onboarding template.")
        data["created_by_id"] = getattr(context.user, "id", None)
        data["lifecycle_status"] = 1
        return data


# ============================================================================
# 6. ONBOARDING SERVICE (EMPLOYEE ONBOARDING TRACKER)
# ============================================================================

@register_service("onboarding")
class OnboardingService(BaseService):
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
        if PolicyEngine.has_capability(context, "onboarding.read") or PolicyEngine.has_capability(context, "onboarding.all"):
            return Q(lifecycle_status=1)

        # Standard employee fallback: restricted to their own onboarding tracker
        return Q(employee=context.user, lifecycle_status=1)

    def before_create(self, context, data):
        from .models import OnboardingTemplate

        emp_id = data.get("employee") or data.get("employee_id") or data.get("employeeId")
        if not emp_id:
            raise ValueError("employee is required for onboarding record.")
        data["employee_id"] = emp_id if not hasattr(emp_id, "id") else emp_id.id

        if not data.get("joining_date") and not data.get("joiningDate"):
            raise ValueError("joining_date is required for onboarding record.")
        data["joining_date"] = data.get("joining_date") or data.get("joiningDate")

        # Auto-populate checklist from matching template if empty
        checklist = list(data.get("checklist") or [])
        if not checklist:
            dept_id = data.get("department_id") or data.get("department")
            desig_id = data.get("designation_id") or data.get("designation")

            template = (
                OnboardingTemplate.objects.filter(
                    department_id=dept_id,
                    designation_id=desig_id,
                    is_active=True
                ).first()
                or OnboardingTemplate.objects.filter(is_default=True, is_active=True).first()
            )

            if template and template.checklist:
                import datetime
                joining_d = datetime.date.fromisoformat(str(data["joining_date"])[:10])
                for t in template.checklist:
                    rel_days = int(t.get("relativeDueDays") or 0)
                    due = joining_d + datetime.timedelta(days=rel_days)
                    checklist.append({
                        "task": t.get("task", ""),
                        "category": t.get("category", "Other"),
                        "documentType": t.get("documentType", ""),
                        "isCompleted": False,
                        "dueDate": due.isoformat(),
                        "verified": False
                    })
                data["checklist"] = checklist

        data["completion_percent"] = Decimal('0.00')
        data["verified_percent"] = Decimal('0.00')
        data["status"] = data.get("status", "Pending")
        data["created_by_id"] = getattr(context.user, "id", None)
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        checklist = list(data.get("checklist") or instance.checklist or [])
        now = timezone.now()

        # Recalculate completion and verification percentages
        if checklist:
            total = len(checklist)
            completed_count = sum(1 for c in checklist if c.get("isCompleted") is True)
            verified_count = sum(1 for c in checklist if c.get("verified") is True)

            comp_pct = round(Decimal((completed_count / total) * 100.0), 2)
            ver_pct = round(Decimal((verified_count / total) * 100.0), 2)

            data["completion_percent"] = comp_pct
            data["verified_percent"] = ver_pct

            if comp_pct == Decimal('100.00') and ver_pct == Decimal('100.00'):
                data["status"] = "Completed"
                data["completed_at"] = now
            elif comp_pct > Decimal('0.00') and instance.status == "Pending":
                data["status"] = "In Progress"

        new_status = data.get("status")
        if new_status and new_status != instance.status:
            if new_status == "Joined":
                data["joined_at"] = now

        return data

