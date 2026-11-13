from django.db import models
from django.conf import settings
from django.utils import timezone
from populate_core.registry import register_model

# ============================================================================
# 1. CONTRIBUTION CATEGORY (MASTER CATALOG)
# ============================================================================

@register_model(
    "contribution_category",
    table_type="master",
    aliases=["contribution_categories", "contributioncategory"]
)
class ContributionCategory(models.Model):
    SCOPE_CHOICES = [
        ("Project Contribution", "Project Contribution"),
        ("Company Contribution", "Company Contribution"),
    ]

    name = models.CharField(max_length=128, unique=True, db_index=True)
    scope = models.CharField(max_length=32, choices=SCOPE_CHOICES, db_index=True)
    base_points = models.FloatField(default=10.0)
    description = models.TextField(blank=True, null=True)
    examples = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, choices=[(1, 'Active'), (0, 'Inactive')], db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contribution_categories"
        ordering = ["scope", "-base_points", "name"]
        indexes = [
            models.Index(fields=["is_active", "scope"]),
            models.Index(fields=["name", "scope"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.scope} - {self.base_points} pts)"


# ============================================================================
# 2. CONTRIBUTION EVALUATION FACTOR (EVALUATION CRITERIA & WEIGHTS)
# ============================================================================

@register_model(
    "contribution_factor",
    table_type="master",
    aliases=["contribution_factors", "contributionfactor"]
)
class ContributionFactor(models.Model):
    code = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=128)
    weight = models.FloatField(default=0.20)  # e.g. 0.20 = 20.00%
    criteria = models.TextField()
    is_active = models.BooleanField(default=True)
    status = models.SmallIntegerField(default=1, choices=[(1, 'Active'), (0, 'Inactive')], db_index=True)
    sort_order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contribution_factors"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.name} ({int(self.weight * 100)}%)"


# ============================================================================
# 3. WORK CONTRIBUTION (IMMUTABLE POINTS LEDGER & FOLLOW-UP STATE MACHINE)
# ============================================================================

@register_model(
    "work_contribution",
    table_type="transaction",
    status_field="lifecycle_status",
    aliases=["work_contributions", "workcontribution"]
)
class WorkContribution(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ("completed", "Completed"),
        ("in_progress", "In Progress"),
        ("stalled", "Stalled"),
        ("on_hold", "On Hold"),
        ("dropped", "Dropped"),
    ]

    APPROVAL_STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="work_contributions",
        db_index=True
    )
    date = models.DateField(default=timezone.now, db_index=True)
    activity = models.TextField()
    client = models.ForeignKey(
        "users.Client",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_contributions"
    )
    project_name = models.CharField(max_length=255, default="Axinix Technologies", db_index=True)
    scope = models.CharField(max_length=32, default="Company Contribution", db_index=True)
    
    primary_category = models.ForeignKey(
        ContributionCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_contributions"
    )
    secondary_category = models.ForeignKey(
        ContributionCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="secondary_contributions"
    )

    worked_days = models.FloatField(default=1.0)
    base_points = models.FloatField(default=10.0)

    # The 6 Rigorous Evaluation Factors (100% total weight)
    factor_effort = models.BooleanField(default=True)       # Effort & Responsibility (20%)
    factor_complexity = models.BooleanField(default=True)   # Complexity & Skill (15%)
    factor_deliverable = models.BooleanField(default=True)  # Deliverable & Completion (25%)
    factor_quality = models.BooleanField(default=True)      # Quality & Reliability (20%)
    factor_evidence = models.BooleanField(default=True)     # Evidence & Ownership (10%)
    factor_outcome = models.BooleanField(default=True)      # Outcome & Long-Term Value (10%)

    factor_percentage = models.FloatField(default=100.0)    # Active factor sum (e.g. 75.0 or 100.0)
    final_points = models.FloatField(default=10.0)         # worked_days * base_points * factor_percentage / 100

    # In-Progress & Follow-Up Lifecycle Tracking
    delivery_status = models.CharField(max_length=32, choices=DELIVERY_STATUS_CHOICES, default="completed", db_index=True)
    parent_activity = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_follow_ups"
    )
    days_open = models.IntegerField(default=0)
    follow_up_count = models.IntegerField(default=0)
    last_follow_up_at = models.DateTimeField(null=True, blank=True)

    evidence_link = models.TextField(blank=True, null=True)
    ai_reasoning = models.TextField(blank=True, null=True)

    approval_status = models.CharField(max_length=32, choices=APPROVAL_STATUS_CHOICES, default="approved", db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_contributions"
    )

    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)  # 1 = active, 0 = soft-deleted
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "work_contributions"
        indexes = [
            models.Index(fields=["lifecycle_status", "user", "date"]),
            models.Index(fields=["lifecycle_status", "scope", "date"]),
            models.Index(fields=["lifecycle_status", "delivery_status"]),
            models.Index(fields=["lifecycle_status", "approval_status"]),
            models.Index(fields=["project_name", "date"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.date}: {self.final_points:.2f} pts ({self.project_name})"
