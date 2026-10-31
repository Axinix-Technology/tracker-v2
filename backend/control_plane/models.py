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
    search_fields=["module_id", "name"],
    status_field="is_active",
    public_fields=["module_id", "name", "description", "collections", "is_active"]
)
class Module(models.Model):
    module_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
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

