from django.conf import settings
from django.db import models
from django.utils import timezone
from populate_core.registry import register_model


# ============================================================================
# 1. JOB CATEGORY (MASTER)
# ============================================================================

@register_model(
    "job_category",
    table_type="master",
    aliases=["job_categories", "jobcategories"],
    search_fields=["name", "description"],
    status_field="is_active",
    public_fields=[]
)
class JobCategory(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=64, default="📁")
    color = models.CharField(max_length=32, default="#6B7280")
    order = models.IntegerField(default=0)
    is_billable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)
    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recruitment_job_categories"
        indexes = [
            models.Index(fields=["is_active", "order"]),
            models.Index(fields=["lifecycle_status", "is_active"]),
        ]
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


# ============================================================================
# 2. JOB TYPE (ACTIVITY CLASSIFICATION / PRODUCTIVITY BENCHMARK)
# ============================================================================

@register_model(
    "job_type",
    table_type="master",
    aliases=["job_types", "jobtypes"],
    search_fields=["name", "description"],
    status_field="is_active",
    public_fields=[]
)
class JobType(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.CASCADE,
        related_name="job_types",
        db_index=True
    )
    icon = models.CharField(max_length=64, default="📋")
    color = models.CharField(max_length=32, default="#6B7280")

    default_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_billable = models.BooleanField(default=True)

    expected_productivity = models.CharField(max_length=32, default="Medium")  # Low, Medium, High, Very High
    expected_output_unit = models.CharField(max_length=64, blank=True, null=True)

    default_delivery_stage = models.CharField(max_length=64, blank=True, null=True)
    auto_set_task_status = models.CharField(max_length=64, blank=True, null=True)

    required_skill_level = models.CharField(max_length=16, blank=True, null=True)  # L1, L2, L3, L4
    allowed_designations = models.ManyToManyField(
        'users.Designation',
        blank=True,
        related_name="allowed_job_types"
    )

    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recruitment_job_types"
        indexes = [
            models.Index(fields=["category", "is_active", "order"]),
            models.Index(fields=["is_active", "order"]),
            models.Index(fields=["lifecycle_status", "is_active"]),
        ]
        ordering = ["category", "order", "name"]

    def __str__(self):
        return f"{self.name} ({self.category.name})"


# ============================================================================
# 3. JOB OPENING (VACANCY POSTING)
# ============================================================================

@register_model(
    "job_opening",
    table_type="transaction",
    aliases=["job_openings", "jobopenings"],
    search_fields=["title", "location", "description"],
    status_field="lifecycle_status",
    public_fields=["title", "location", "job_type", "experience_range", "description", "requirements", "openings", "published_at"]
)
class JobOpening(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    department = models.ForeignKey(
        'users.Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="job_openings",
        db_index=True
    )
    designation = models.ForeignKey(
        'users.Designation',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="job_openings",
        db_index=True
    )
    location = models.CharField(max_length=128, blank=True, null=True)
    job_type = models.CharField(max_length=32, default="Full-Time")  # Full-Time, Part-Time, Contract, Intern
    experience_range = models.CharField(max_length=64, blank=True, null=True)
    salary_range = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)

    openings = models.IntegerField(default=1)
    filled = models.IntegerField(default=0)

    status = models.CharField(
        max_length=32,
        default="Draft",
        db_index=True,
        help_text="Draft, Published, On Hold, Closed, Filled"
    )
    published_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_job_openings"
    )
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recruitment_job_openings"
        indexes = [
            models.Index(fields=["status", "department"]),
            models.Index(fields=["lifecycle_status", "status", "-created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status}) - {self.filled}/{self.openings} Filled"


# ============================================================================
# 4. CANDIDATE (APPLICANT TRACKING SYSTEM)
# ============================================================================

@register_model(
    "candidate",
    table_type="transaction",
    aliases=["candidates"],
    search_fields=["first_name", "last_name", "email", "phone", "application_id"],
    status_field="lifecycle_status",
    public_fields=[]
)
class Candidate(models.Model):
    first_name = models.CharField(max_length=128, db_index=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    linkedin_url = models.URLField(max_length=512, blank=True, null=True)
    resume_url = models.TextField(blank=True, null=True)

    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=16, blank=True, null=True)
    marital_status = models.CharField(max_length=32, blank=True, null=True)
    father_name = models.CharField(max_length=128, blank=True, null=True)
    mother_name = models.CharField(max_length=128, blank=True, null=True)
    address = models.JSONField(default=dict)

    application_id = models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True)
    job_opening = models.ForeignKey(
        JobOpening,
        on_delete=models.CASCADE,
        related_name="candidates",
        db_index=True
    )
    source = models.CharField(max_length=64, default="Direct")  # Career Page, Referral, LinkedIn, Job Portal, Direct, Other
    referred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referred_candidates"
    )

    stage = models.CharField(
        max_length=32,
        default="Applied",
        db_index=True,
        help_text="Applied, Screening, Interview, Offered, Hired, Rejected, Withdrawn"
    )
    stage_history = models.JSONField(default=list)

    # Interview Details
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.CharField(max_length=32, blank=True, null=True)
    interview_type = models.CharField(max_length=32, default="In-Person")
    interviewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="interviewed_candidates"
    )
    interview_notes = models.TextField(blank=True, null=True)
    interview_rating = models.SmallIntegerField(null=True, blank=True)

    # Offer Details
    offered_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    offer_letter_url = models.TextField(blank=True, null=True)
    offer_expiry_date = models.DateField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)

    rejection_reason = models.TextField(blank=True, null=True)
    rejection_mail_sent = models.BooleanField(default=False)

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="originating_candidates"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_candidates"
    )
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recruitment_candidates"
        indexes = [
            models.Index(fields=["job_opening", "stage"]),
            models.Index(fields=["stage", "-created_at"]),
            models.Index(fields=["lifecycle_status", "stage", "job_opening"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name or ''}".strip()
        return f"{full_name} ({self.application_id or 'No ID'}) - {self.stage}"


# ============================================================================
# 5. ONBOARDING TEMPLATE (CHECKLIST BLUEPRINT)
# ============================================================================

@register_model(
    "onboarding_template",
    table_type="master",
    aliases=["onboarding_templates", "onboardingtemplates"],
    search_fields=["title"],
    status_field="is_active",
    public_fields=[]
)
class OnboardingTemplate(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    department = models.ForeignKey(
        'users.Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="onboarding_templates",
        db_index=True
    )
    designation = models.ForeignKey(
        'users.Designation',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="onboarding_templates",
        db_index=True
    )
    employment_type = models.CharField(max_length=32, default="All", db_index=True)  # Full-Time, Contract, Intern, All

    checklist = models.JSONField(
        default=list,
        help_text="Template checklist items: [{ task, category, documentType, isRequired, relativeDueDays }]"
    )

    is_active = models.BooleanField(default=True, db_index=True)
    is_default = models.BooleanField(default=False, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_onboarding_templates"
    )
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recruitment_onboarding_templates"
        indexes = [
            models.Index(fields=["department", "designation", "employment_type", "is_active"]),
            models.Index(fields=["lifecycle_status", "is_active"]),
        ]
        ordering = ["-is_default", "title"]

    def __str__(self):
        return f"{self.title} ({self.employment_type})"


# ============================================================================
# 6. ONBOARDING (EMPLOYEE ONBOARDING TRACKER)
# ============================================================================

@register_model(
    "onboarding",
    table_type="transaction",
    aliases=["onboardings"],
    search_fields=["employee__username", "employee__first_name", "employee__last_name", "remarks"],
    status_field="lifecycle_status",
    public_fields=[]
)
class Onboarding(models.Model):
    employee = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="onboarding",
        db_index=True
    )
    candidate = models.ForeignKey(
        Candidate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="onboardings"
    )
    joining_date = models.DateField(db_index=True)
    department = models.ForeignKey(
        'users.Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="onboarding_records"
    )
    designation = models.ForeignKey(
        'users.Designation',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="onboarding_records"
    )
    reporting_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="supervised_onboardings"
    )

    checklist = models.JSONField(
        default=list,
        help_text="Checklist items: [{ task, category, isCompleted, completedAt, completedBy, dueDate, note, documentType, fileUrl, verified, verifiedAt, verifiedBy, rejectionReason }]"
    )
    completion_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    verified_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    status = models.CharField(
        max_length=32,
        default="Pending",
        db_index=True,
        help_text="Pending, In Progress, Documents Pending, Verification Pending, Ready To Join, Joined, Completed, Cancelled, Postponed, No Show"
    )

    target_completion_date = models.DateField(null=True, blank=True, db_index=True)
    sla_breached = models.BooleanField(default=False, db_index=True)
    sla_breached_at = models.DateTimeField(null=True, blank=True)

    joined_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    postponed_to_date = models.DateField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    welcome_mail_sent = models.BooleanField(default=False)
    asset_allocated = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_onboardings"
    )
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recruitment_onboardings"
        indexes = [
            models.Index(fields=["status", "-joining_date"]),
            models.Index(fields=["target_completion_date", "status"]),
            models.Index(fields=["lifecycle_status", "status", "joining_date"]),
        ]
        ordering = ["-joining_date", "-id"]

    def __str__(self):
        return f"Onboarding: {self.employee} ({self.status}) - {self.completion_percent}%"

