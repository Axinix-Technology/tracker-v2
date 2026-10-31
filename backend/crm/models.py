from django.conf import settings
from django.db import models
from django.utils import timezone
from populate_core.registry import register_model


# ============================================================================
# 1. LEAD TYPE (MASTER)
# ============================================================================

@register_model(
    "lead_type",
    table_type="master",
    aliases=["lead_types", "leadtypes"],
    search_fields=["name", "description"],
    status_field="status",
    public_fields=[]
)
class LeadType(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=16, default="Active", db_index=True)  # Active, Inactive
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crm_lead_types"
        indexes = [
            models.Index(fields=["status", "name"]),
            models.Index(fields=["lifecycle_status", "status"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name


# ============================================================================
# 2. REFERENCE TYPE (MASTER)
# ============================================================================

@register_model(
    "reference_type",
    table_type="master",
    aliases=["reference_types", "referencetypes"],
    search_fields=["name", "description"],
    status_field="status",
    public_fields=[]
)
class ReferenceType(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=16, default="Active", db_index=True)  # Active, Inactive
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crm_reference_types"
        indexes = [
            models.Index(fields=["status", "name"]),
            models.Index(fields=["lifecycle_status", "status"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name


# ============================================================================
# 3. CONTACT (PROSPECT / LEAD)
# ============================================================================

@register_model(
    "contact",
    table_type="transaction",
    aliases=["contacts"],
    search_fields=["first_name", "last_name", "company_name", "email", "phone"],
    status_field="lifecycle_status",
    public_fields=[]
)
class Contact(models.Model):
    first_name = models.CharField(max_length=128, db_index=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    email = models.EmailField(blank=True, null=True, db_index=True)
    phone = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    designation = models.CharField(max_length=128, blank=True, null=True)
    source = models.CharField(max_length=128, blank=True, null=True)

    lead_type = models.ForeignKey(LeadType, null=True, blank=True, on_delete=models.SET_NULL, related_name="contacts")
    reference_type = models.ForeignKey(ReferenceType, null=True, blank=True, on_delete=models.SET_NULL, related_name="contacts")
    notes = models.TextField(blank=True, null=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_contacts",
        db_index=True
    )
    contacted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contacted_records",
        db_index=True
    )
    contacted_at = models.DateTimeField(null=True, blank=True)

    contact_history = models.JSONField(
        default=list,
        help_text="Historical log: [{ contactedBy, contactedAt, method, notes, outcome }]"
    )

    status = models.CharField(
        max_length=32,
        default="New",
        db_index=True,
        help_text="New, Contacted, Qualified, Converted, Lost"
    )
    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)

    converted_client = models.ForeignKey(
        'users.Client',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="originating_contacts"
    )
    tags = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crm_contacts"
        indexes = [
            models.Index(fields=["status", "assigned_to"]),
            models.Index(fields=["company_name", "status"]),
            models.Index(fields=["lifecycle_status", "status", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name or ''}".strip()
        return f"{full_name} ({self.company_name or 'Independent'}) - {self.status}"


# ============================================================================
# 4. OPPORTUNITY (DEAL / SALES PIPELINE)
# ============================================================================

@register_model(
    "opportunity",
    table_type="transaction",
    aliases=["opportunities"],
    search_fields=["name", "account__name", "competitor", "lost_reason"],
    status_field="lifecycle_status",
    public_fields=[]
)
class Opportunity(models.Model):
    account = models.ForeignKey(
        'users.Client',
        on_delete=models.CASCADE,
        related_name="opportunities",
        db_index=True
    )
    contact = models.ForeignKey(
        Contact,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="opportunities",
        db_index=True
    )
    name = models.CharField(max_length=255, db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_opportunities",
        db_index=True
    )

    stage = models.CharField(
        max_length=32,
        default="New",
        db_index=True,
        help_text="New, Discovery, Proposal, Negotiation, Won, Lost"
    )
    expected_value = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    probability = models.SmallIntegerField(default=10, help_text="0-100 percentage probability")

    expected_close_date = models.DateField(null=True, blank=True, db_index=True)
    actual_close_date = models.DateField(null=True, blank=True)

    quotation = models.ForeignKey(
        'billing.Quotation',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="linked_opportunities"
    )
    contract = models.ForeignKey(
        'billing.OrderAcknowledgement',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="linked_opportunities"
    )
    project_type = models.ForeignKey(
        'users.ProjectType',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="opportunities"
    )

    lost_reason = models.TextField(blank=True, null=True)
    competitor = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list)

    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_opportunities"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crm_opportunities"
        indexes = [
            models.Index(fields=["account", "stage"]),
            models.Index(fields=["owner", "stage"]),
            models.Index(fields=["stage", "expected_close_date"]),
            models.Index(fields=["lifecycle_status", "stage", "-expected_value"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.account.name}) - {self.stage} [{self.expected_value}]"


# ============================================================================
# 5. CRM ACTIVITY (CHRONOLOGICAL INTERACTION LOG)
# ============================================================================

@register_model(
    "crm_activity",
    table_type="transaction",
    aliases=["crm_activities", "crmactivities"],
    search_fields=["content"],
    status_field="lifecycle_status",
    public_fields=[]
)
class CRMActivity(models.Model):
    client = models.ForeignKey(
        'users.Client',
        on_delete=models.CASCADE,
        related_name="crm_activities",
        db_index=True
    )
    type = models.CharField(
        max_length=32,
        default="Note",
        db_index=True,
        help_text="Call, Meeting, Email, Note, Task, System, Other"
    )
    content = models.TextField()
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="performed_crm_activities",
        db_index=True
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    metadata = models.JSONField(default=dict)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "crm_activities"
        indexes = [
            models.Index(fields=["client", "-timestamp"]),
            models.Index(fields=["lifecycle_status", "client", "-timestamp"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.type}] {self.client.name}: {self.content[:40]}"


# ============================================================================
# 6. CRM MEETING (CALENDAR SCHEDULE & OUTCOME)
# ============================================================================

@register_model(
    "crm_meeting",
    table_type="transaction",
    aliases=["crm_meetings", "crmmeetings"],
    search_fields=["title", "description", "outcome"],
    status_field="lifecycle_status",
    public_fields=[]
)
class CRMMeeting(models.Model):
    client = models.ForeignKey(
        'users.Client',
        on_delete=models.CASCADE,
        related_name="crm_meetings",
        db_index=True
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    scheduled_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=32,
        default="Scheduled",
        db_index=True,
        help_text="Scheduled, Started, Completed, Cancelled"
    )
    outcome = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="crm_meetings",
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_crm_meetings"
    )

    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crm_meetings"
        indexes = [
            models.Index(fields=["scheduled_time", "status"]),
            models.Index(fields=["client", "status"]),
            models.Index(fields=["lifecycle_status", "status", "scheduled_time"]),
        ]
        ordering = ["-scheduled_time"]

    def __str__(self):
        return f"Meeting: {self.title} ({self.client.name}) - {self.status}"

