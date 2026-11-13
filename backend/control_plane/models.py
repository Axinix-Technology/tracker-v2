from django.conf import settings
from django.db import models
from django.utils import timezone
from populate_core.registry import register_model


# ============================================================================
# 1. TENANT (MULTI-TENANT DIRECTORY)
# ============================================================================

@register_model(
    "tenant",
    table_type="system",
    aliases=["tenants"],
    search_fields=["tenant_id", "name", "subdomain"],
    status_field="lifecycle_status",
    public_fields=["tenant_id", "name", "subdomain", "plan", "status"]
)
class Tenant(models.Model):
    tenant_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    subdomain = models.CharField(max_length=128, unique=True, db_index=True)
    database_name = models.CharField(max_length=128, unique=True)
    plan = models.CharField(max_length=64, default="Enterprise")
    status = models.CharField(max_length=32, default="Active", db_index=True)  # Active, Suspended, Provisioning, Deleted
    enabled_modules = models.JSONField(
        default=list,
        help_text="e.g. ['hrms', 'attendance', 'payroll', 'billing', 'crm', 'recruitment']"
    )
    settings = models.JSONField(default=dict)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "control_plane_tenants"
        indexes = [
            models.Index(fields=["status", "subdomain"]),
            models.Index(fields=["lifecycle_status", "status"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} [{self.subdomain}] ({self.status})"


# ============================================================================
# 2. USER LOGIN (CENTRALIZED CREDENTIAL & ROUTING DIRECTORY)
# ============================================================================

@register_model(
    "user_login",
    table_type="system",
    aliases=["user_logins", "userlogins"],
    search_fields=["email"],
    status_field="is_active",
    public_fields=[]
)
class UserLogin(models.Model):
    email = models.EmailField(db_index=True)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="user_logins",
        db_index=True
    )
    user_id = models.IntegerField(db_index=True, help_text="Primary key of user inside tenant database")
    is_superadmin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    last_login = models.DateTimeField(null=True, blank=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "control_plane_user_logins"
        unique_together = ("email", "tenant")
        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["tenant", "is_active"]),
        ]

    def __str__(self):
        return f"{self.email} -> {self.tenant.subdomain} (User #{self.user_id})"


# ============================================================================
# 3. MODULE (GLOBAL MODULE ENTITLEMENT CATALOG)
# ============================================================================

@register_model(
    "module",
    table_type="system",
    aliases=["modules"],
    search_fields=["module_id", "name", "category"],
    status_field="is_active",
    public_fields=[
        "module_id",
        "name",
        "description",
        "category",
        "icon",
        "price_per_user_monthly",
        "features",
        "prerequisites",
        "collections",
        "is_active",
    ]
)
class Module(models.Model):
    module_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=64, default="Operations", db_index=True)
    icon = models.CharField(max_length=64, default="Box")
    price_per_user_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=30.00)
    description = models.TextField(blank=True, null=True)
    features = models.JSONField(
        default=list,
        help_text="Key bullet points for storefront marketing"
    )
    prerequisites = models.JSONField(
        default=list,
        help_text="e.g. ['attendance'] required before payroll"
    )
    collections = models.JSONField(
        default=list,
        help_text="Registered model names granted under this module"
    )
    is_active = models.BooleanField(default=True, db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "control_plane_modules"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} [{self.module_id}]"


# ============================================================================
# 4. PROVISIONING RUN (TENANT DATABASE MIGRATION & PROVISIONING LOG)
# ============================================================================

@register_model(
    "provisioning_run",
    table_type="system",
    aliases=["provisioning_runs", "provisioningruns"],
    search_fields=["database_name", "error_message"],
    status_field="lifecycle_status",
    public_fields=[]
)
class ProvisioningRun(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="provisioning_runs",
        db_index=True
    )
    database_name = models.CharField(max_length=128)
    status = models.CharField(max_length=32, default="Pending", db_index=True)  # Pending, In Progress, Completed, Failed
    steps_completed = models.JSONField(default=list)
    error_message = models.TextField(blank=True, null=True)
    initiated_by = models.CharField(max_length=128, default="System")
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)

    class Meta:
        db_table = "control_plane_provisioning_runs"
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["started_at", "status"]),
        ]
        ordering = ["-started_at"]

    def __str__(self):
        return f"Provisioning for {self.tenant.subdomain} - {self.status}"


# ============================================================================
# 5. PLATFORM ROLE (PLATFORM CONTROL PLANE RBAC)
# ============================================================================

@register_model(
    "platform_role",
    table_type="system",
    aliases=["platform_roles", "platformroles"],
    search_fields=["role_id", "name"],
    status_field="lifecycle_status",
    public_fields=["role_id", "name", "description", "is_root_admin", "is_active"]
)
class PlatformRole(models.Model):
    role_id = models.CharField(max_length=64, unique=True, db_index=True)  # e.g. root_admin, management_viewer, support_engineer
    name = models.CharField(max_length=128, db_index=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_root_admin = models.BooleanField(default=False, db_index=True)      # ONLY True for Root Admin
    permissions = models.JSONField(
        default=dict,
        help_text="e.g. {'tenants': ['read'], 'metrics': ['read'], 'modules': ['read']} or {'*': ['*']}"
    )
    is_active = models.BooleanField(default=True, db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "control_plane_platform_roles"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} [{self.role_id}] (Root={self.is_root_admin})"


# ============================================================================
# 6. PLATFORM USER (DEDICATED PLATFORM CONTROL PLANE OPERATORS)
# ============================================================================

@register_model(
    "platform_user",
    table_type="system",
    aliases=["platform_users", "platformusers"],
    search_fields=["username", "email", "first_name", "last_name"],
    status_field="is_active",
    public_fields=["id", "username", "email", "first_name", "last_name", "role", "is_active"]
)
class PlatformUser(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    role = models.ForeignKey(
        PlatformRole,
        on_delete=models.PROTECT,
        related_name="platform_users",
        db_index=True
    )
    is_active = models.BooleanField(default=True, db_index=True)
    last_login = models.DateTimeField(null=True, blank=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "control_plane_platform_users"
        ordering = ["username"]

    def __str__(self):
        return f"{self.username} ({self.email}) [{self.role.name}]"

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


# ============================================================================
# 7. RETENTION POLICY (STORAGE & DATA RETENTION RULES)
# ============================================================================

@register_model(
    "retention_policy",
    table_type="system",
    aliases=["retention_policies", "retentionpolicies"],
    search_fields=["policy_id", "module_id"],
    status_field="lifecycle_status",
    public_fields=["policy_id", "module_id", "grace_period_days", "storage_backend", "is_auto_purge_enabled"]
)
class RetentionPolicy(models.Model):
    policy_id = models.CharField(max_length=64, unique=True, db_index=True)
    module_id = models.CharField(max_length=64, default="all", db_index=True)
    grace_period_days = models.PositiveIntegerField(default=90)
    notification_days = models.JSONField(
        default=list,
        help_text="Days prior to purge to send notification emails e.g. [60, 80, 89]"
    )
    storage_backend = models.CharField(max_length=32, default="local")  # local, s3, r2
    archive_tier = models.CharField(max_length=32, default="cold_zip")   # cold_zip, glacier, coldline
    is_auto_purge_enabled = models.BooleanField(default=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "control_plane_retention_policies"
        ordering = ["module_id"]

    def __str__(self):
        return f"RetentionPolicy [{self.module_id}] - {self.grace_period_days}d"


# ============================================================================
# 8. RETENTION EVENT (DEGRADED MODULE LIFECYCLE & PURGE LEDGER)
# ============================================================================

@register_model(
    "retention_event",
    table_type="system",
    aliases=["retention_events", "retentionevents"],
    search_fields=["module_id", "status"],
    status_field="lifecycle_status",
    public_fields=[
        "id", "tenant", "module_id", "status", "degraded_at",
        "purge_scheduled_at", "reclaimed_bytes", "purged_at"
    ]
)
class RetentionEvent(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="retention_events",
        db_index=True
    )
    module_id = models.CharField(max_length=64, db_index=True)
    status = models.CharField(
        max_length=32,
        default="Scheduled",
        db_index=True
    )  # Scheduled, Notified, Archived, Purged, Cancelled
    degraded_at = models.DateTimeField(default=timezone.now, db_index=True)
    purge_scheduled_at = models.DateTimeField(db_index=True)
    notifications_sent = models.JSONField(default=list)
    archive_file_url = models.CharField(max_length=512, blank=True, null=True)
    reclaimed_bytes = models.BigIntegerField(default=0)
    reclaimed_files_count = models.PositiveIntegerField(default=0)
    reclaimed_db_rows_count = models.PositiveIntegerField(default=0)
    purged_at = models.DateTimeField(null=True, blank=True)
    initiated_by = models.CharField(max_length=64, default="System_Automated")
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "control_plane_retention_events"
        indexes = [
            models.Index(fields=["tenant", "module_id", "status"]),
            models.Index(fields=["purge_scheduled_at", "status"]),
        ]
        ordering = ["-purge_scheduled_at"]

    def __str__(self):
        return f"{self.tenant.subdomain} [{self.module_id}] - {self.status}"



