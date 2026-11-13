from django.conf import settings
from django.db import models
from django.utils import timezone
from populate_core.registry import register_model


# ============================================================================
# 1. STATUS CONFIG (STATUS MASTER)
# ============================================================================

@register_model(
    "status_config",
    table_type="master",
    aliases=["status_configs", "status_configss"],
    search_fields=["model_name", "label"],
    status_field="status",
    public_fields=["model_name", "label", "meta_statuses", "workflow_statuses"]
)
class StatusConfig(models.Model):
    model_name = models.CharField(max_length=128, unique=True, db_index=True)
    label = models.CharField(max_length=128)
    meta_statuses = models.JSONField(
        default=list,
        help_text="Key, label, color, order, isDefault"
    )
    workflow_statuses = models.JSONField(
        default=list,
        help_text="Key, label, color, order, isDefault, isTerminal, isSequential"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_status_configs"
        ordering = ["model_name"]

    def __str__(self):
        return f"{self.label} ({self.model_name})"


# ============================================================================
# 2. STATUS MAPPING (CROSS-MODEL STATE SYNC)
# ============================================================================

@register_model(
    "status_mapping",
    table_type="master",
    aliases=["status_mappings", "statusmappings"],
    search_fields=["source_model", "target_model"],
    status_field="is_active",
    public_fields=[]
)
class StatusMapping(models.Model):
    source_model = models.CharField(max_length=128, db_index=True)
    target_model = models.CharField(max_length=128, db_index=True)
    link_field = models.CharField(max_length=128, default="linkedTicketId")
    reverse_link_field = models.CharField(max_length=128, default="linkedTaskId")
    mappings = models.JSONField(
        default=list,
        help_text="List of status mappings: [{ sourceStatus, targetStatus }]"
    )
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_status_mappings"
        unique_together = ("source_model", "target_model")
        indexes = [
            models.Index(fields=["source_model", "target_model"]),
            models.Index(fields=["is_active", "status"]),
        ]

    def __str__(self):
        return f"Mapping: {self.source_model} -> {self.target_model}"


# ============================================================================
# 3. EMAIL CONFIG (SMTP CREDENTIAL REGISTRY)
# ============================================================================

@register_model(
    "email_config",
    table_type="system",
    aliases=["email_configs", "emailconfigs"],
    search_fields=["host", "from_name", "from_email"],
    status_field="enabled",
    public_fields=["service", "host", "port", "secure", "from_name", "from_email", "enabled"]
)
class EmailConfig(models.Model):
    service = models.CharField(max_length=32, default="gmail")
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=587)
    secure = models.BooleanField(default=False)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    from_name = models.CharField(max_length=128)
    from_email = models.EmailField()
    enabled = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_email_configs"

    def __str__(self):
        return f"EmailConfig: {self.from_email} ({self.host}:{self.port})"


# ============================================================================
# 4. SERVICE PROVIDER (VENDOR / CONTRACTOR REGISTRY)
# ============================================================================

@register_model(
    "service_provider",
    table_type="master",
    aliases=["service_providers", "serviceproviders"],
    search_fields=["name", "contact_person", "email", "phone", "gst_in"],
    status_field="lifecycle_status",
    public_fields=[]
)
class ServiceProvider(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    contact_person = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    address = models.JSONField(default=dict)

    gst_in = models.CharField(max_length=32, blank=True, null=True)
    pan_number = models.CharField(max_length=32, blank=True, null=True)
    bank_details = models.JSONField(default=dict)

    services = models.ManyToManyField(
        'users.ProjectType',
        blank=True,
        related_name="service_providers"
    )
    status = models.CharField(max_length=16, default="Active", db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_service_providers"
        indexes = [
            models.Index(fields=["status", "name"]),
            models.Index(fields=["lifecycle_status", "status"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name


# ============================================================================
# 5. RELEASE NOTE (PRODUCT CHANGELOG & VERSION BADGE)
# ============================================================================

@register_model(
    "release_note",
    table_type="master",
    aliases=["release_notes", "releasenotes"],
    search_fields=["version", "title", "tagline"],
    status_field="is_published",
    public_fields=["version", "release_date", "title", "tagline", "type", "is_latest", "is_published", "categories"]
)
class ReleaseNote(models.Model):
    version = models.CharField(max_length=64, db_index=True)
    release_date = models.DateTimeField(default=timezone.now, db_index=True)
    title = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=64, default="Feature & Maintenance Release")

    is_latest = models.BooleanField(default=False, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)
    categories = models.JSONField(
        default=dict,
        help_text="Features, improvements, security, fixes"
    )
    seen_by = models.JSONField(default=list, help_text="[{ employeeId, viewedAt }]")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_release_notes"
    )
    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_release_notes"
        indexes = [
            models.Index(fields=["is_published", "is_latest"]),
            models.Index(fields=["version", "is_published"]),
        ]
        ordering = ["-release_date", "-id"]

    def __str__(self):
        return f"v{self.version}: {self.title}"


# ============================================================================
# 6. RESOURCE (CANONICAL PERMISSION & ENTITY REGISTRY)
# ============================================================================

@register_model(
    "resource",
    table_type="master",
    aliases=["resources"],
    search_fields=["key", "display_name", "module"],
    status_field="is_active",
    public_fields=["key", "model_name", "display_name", "module", "description", "is_active"]
)
class Resource(models.Model):
    key = models.CharField(max_length=128, unique=True, db_index=True, help_text="Frontend can() target key e.g. leave, ticket")
    model_name = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    display_name = models.CharField(max_length=128)
    module = models.CharField(max_length=64, default="general", db_index=True)
    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True, db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_resources"
        indexes = [
            models.Index(fields=["module", "is_active"]),
            models.Index(fields=["lifecycle_status", "is_active"]),
        ]
        ordering = ["module", "key"]

    def __str__(self):
        return f"{self.display_name} [{self.key}]"


# ============================================================================
# 7. WORKFLOW (CONFIGURABLE MULTI-STEP APPROVAL ENGINE)
# ============================================================================

@register_model(
    "workflow",
    table_type="master",
    aliases=["workflows"],
    search_fields=["name", "model_name", "trigger_type"],
    status_field="is_active",
    public_fields=[]
)
class Workflow(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    model_name = models.CharField(max_length=128, db_index=True)
    trigger_type = models.CharField(max_length=64, db_index=True)  # Approval, Escalation, Onboarding

    conditions = models.JSONField(default=dict, help_text="{ departmentId, priorityLevel }")
    steps = models.JSONField(
        default=list,
        help_text="List of steps: [{ stepOrder, timeoutHours, actorType, specificRoleId, specificUserId, actions, updateStatusTo, requiredDocumentType }]"
    )

    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_workflows"
    )
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_workflows"
        indexes = [
            models.Index(fields=["model_name", "trigger_type", "is_active"]),
            models.Index(fields=["lifecycle_status", "is_active"]),
        ]
        ordering = ["model_name", "name"]

    def __str__(self):
        return f"Workflow: {self.name} ({self.model_name} / {self.trigger_type})"


# ============================================================================
# 8. PRODUCT (COMMERCIAL PRODUCT CATALOG)
# ============================================================================

@register_model(
    "product",
    table_type="master",
    aliases=["products"],
    search_fields=["name", "code", "description"],
    status_field="is_active",
    public_fields=["name", "code", "description", "category", "unit_price", "tax_rate", "is_active"]
)
class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    code = models.CharField(max_length=64, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=128, default="Software")

    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)

    is_active = models.BooleanField(default=True, db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_products"
        indexes = [
            models.Index(fields=["is_active", "name"]),
            models.Index(fields=["lifecycle_status", "is_active"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} [{self.code}] - {self.unit_price}"


# ============================================================================
# 9. SHOWCASE & WEBSITE CMS MODELS
# ============================================================================
from .showcase_models import (
    SiteSectionContent,
    CompanyProfile,
    ShowcaseAnnouncement,
    ShowcaseStat,
    ShowcaseSolution,
    ShowcaseIndustry,
    ShowcaseService,
    ShowcasePortfolio,
    ShowcaseTestimonial,
    ShowcaseCategory,
    ShowcaseProduct,
    WebsiteInquiry,
)

