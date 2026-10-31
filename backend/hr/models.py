from django.db import models
from django.conf import settings
from django.utils import timezone
from populate_core.registry import register_model


# ============================================================================
# 1. EMPLOYEE DOCUMENTS (VERIFICATION & COMPLIANCE)
# ============================================================================

@register_model(
    "employee_document",
    table_type="transaction",
    aliases=["employee_documents", "employeedocument"]
)
class EmployeeDocument(models.Model):
    DOCUMENT_TYPES = [
        ("Resume", "Resume"),
        ("Photo", "Photo"),
        ("PAN", "PAN Card"),
        ("Aadhaar", "Aadhaar Card"),
        ("Passport", "Passport"),
        ("Degree", "Degree Certificate"),
        ("Experience Letter", "Experience Letter"),
        ("Relieving Letter", "Relieving Letter"),
        ("Offer Letter", "Offer Letter"),
        ("Joining Letter", "Joining Letter"),
        ("Bank Proof", "Bank Proof"),
        ("Medical Certificate", "Medical Certificate"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_documents"
    )
    document_type = models.CharField(
        max_length=64,
        choices=DOCUMENT_TYPES,
        db_index=True
    )
    file_url = models.CharField(max_length=512)
    uploaded_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default="Pending",
        db_index=True
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_documents"
    )
    remarks = models.TextField(blank=True, null=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "employee_documents"
        indexes = [
            models.Index(fields=["lifecycle_status", "employee", "status"]),
            models.Index(fields=["lifecycle_status", "document_type", "status"]),
            models.Index(fields=["employee", "document_type"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.document_type} ({self.status})"

    @property
    def employeeId(self):
        return self.employee

    @property
    def documentType(self):
        return self.document_type

    @property
    def fileUrl(self):
        return self.file_url

    @property
    def uploadedAt(self):
        return self.uploaded_at

    @property
    def approvedBy(self):
        return self.approved_by


# ============================================================================
# 2. EMPLOYEE LIFECYCLE HISTORY (AUDIT & PROGRESSION)
# ============================================================================

@register_model(
    "employee_lifecycle_history",
    table_type="transaction",
    aliases=["employee_lifecycle_histories", "employee_life_cycle_histories", "employeelifecyclehistory"],
    allow_direct_update=False,
    allow_direct_delete=False
)
class EmployeeLifecycleHistory(models.Model):
    CHANGE_TYPES = [
        ("InitialBaseline", "Initial Baseline"),
        ("Promotion", "Promotion"),
        ("Transfer", "Transfer"),
        ("SalaryRevision", "Salary Revision"),
        ("DesignationChange", "Designation Change"),
        ("DepartmentChange", "Department Change"),
        ("ManagerChange", "Manager Change"),
        ("RoleChange", "Role Change"),
        ("StatusChange", "Status Change"),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lifecycle_histories"
    )
    change_type = models.CharField(
        max_length=64,
        choices=CHANGE_TYPES,
        db_index=True
    )
    effective_date = models.DateField(default=timezone.now, db_index=True)
    previous_value = models.JSONField(default=dict, blank=True, null=True)
    new_value = models.JSONField(default=dict)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_lifecycle_changes"
    )
    reason = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    status = models.SmallIntegerField(default=1, choices=[(1, "Active"), (0, "Inactive")], db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employee_life_cycle_histories"
        indexes = [
            models.Index(fields=["lifecycle_status", "employee", "effective_date"]),
            models.Index(fields=["lifecycle_status", "change_type", "effective_date"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.change_type} on {self.effective_date}"

    @property
    def employeeId(self):
        return self.employee

    @property
    def changeType(self):
        return self.change_type

    @property
    def effectiveDate(self):
        return self.effective_date

    @property
    def changedBy(self):
        return self.changed_by


# ============================================================================
# 3. HR POLICIES & ACKNOWLEDGMENTS
# ============================================================================

@register_model(
    "hr_policy",
    table_type="master",
    aliases=["hr_policies", "hrpolicy"]
)
class HRPolicy(models.Model):
    CATEGORIES = [
        ("Leave Policy", "Leave Policy"),
        ("Code of Conduct", "Code of Conduct"),
        ("Attendance", "Attendance"),
        ("Compensation", "Compensation"),
        ("Benefits", "Benefits"),
        ("Performance", "Performance"),
        ("General", "General"),
    ]

    title = models.CharField(max_length=255, db_index=True)
    category = models.CharField(max_length=64, choices=CATEGORIES, db_index=True)
    content = models.TextField()
    version = models.CharField(max_length=32, default="1.0")
    status = models.CharField(max_length=32, default="Draft", db_index=True)
    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    effective_date = models.DateField(default=timezone.now, db_index=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    applicable_to = models.JSONField(default=list)  # ["All Employees", "Management", "HR", "Specific Department", "Specific Role"]
    departments = models.ManyToManyField("users.Department", blank=True, related_name="hr_policies")
    roles = models.ManyToManyField("users.Role", blank=True, related_name="hr_policies")
    attachments = models.JSONField(default=list)  # [{ "filename": str, "path": str, "uploadedAt": iso }]
    acknowledgments = models.JSONField(default=list)  # [{ "employeeId": int, "acknowledgedAt": iso, "ipAddress": str }]
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_hr_policies"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_hr_policies"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    tags = models.JSONField(default=list)
    is_public = models.BooleanField(default=True)
    requires_acknowledgment = models.BooleanField(default=False)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_policies"
        indexes = [
            models.Index(fields=["lifecycle_status", "category", "status"]),
            models.Index(fields=["lifecycle_status", "status", "created_at"]),
            models.Index(fields=["lifecycle_status", "effective_date"]),
        ]

    def __str__(self):
        return f"{self.title} (v{self.version})"

    @property
    def effectiveDate(self):
        return self.effective_date

    @property
    def expiryDate(self):
        return self.expiry_date

    @property
    def createdBy(self):
        return self.created_by

    @property
    def approvedBy(self):
        return self.approved_by

    @property
    def requiresAcknowledgment(self):
        return self.requires_acknowledgment

    @property
    def isPublic(self):
        return self.is_public


# ============================================================================
# 4. USER OVERRIDE (UI CAPABILITY GATES PER USER)
# ============================================================================

@register_model(
    "user_override",
    table_type="master",
    aliases=["user_overrides", "useroverride"]
)
class UserOverride(models.Model):
    """
    User-specific UI capability overrides for frontend visibility.
    Controls granular UI display without modifying underlying access policies.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="capability_overrides"
    )
    overrides = models.JSONField(default=list)  # [{ "capabilityKey": str, "effect": "allow" | "deny" }]
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_overrides"

    def __str__(self):
        return f"UI Overrides for {self.user}"

    @property
    def userId(self):
        return self.user

