import json
import logging
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from control_plane.models import Tenant, PlatformRole, PlatformUser
from users.models import Role

User = get_user_model()
logger = logging.getLogger("modular_entitlements_test")


class ModularEntitlementsAuditTestCase(TestCase):
    """
    Test suite verifying the Two-Plane Decoupled Architecture:
    1. Platform Plane: PlatformRootAdmin (Full) vs PlatformManagementViewer (Read-Only)
    2. Client Plane: ClientSuperAdmin is blocked from Platform models
    3. Modular Entitlements: Purchase, Upgrade, Degrade with Zero Permission Leakage
    """

    def setUp(self):
        # 1. Platform Roles
        self.role_root, _ = PlatformRole.objects.get_or_create(
            role_id="root_admin",
            defaults={"name": "Platform Root Admin", "is_root_admin": True, "permissions": {"*": ["*"]}}
        )
        self.role_viewer, _ = PlatformRole.objects.get_or_create(
            role_id="management_viewer",
            defaults={"name": "Management Viewer", "is_root_admin": False, "permissions": {"tenants": ["read"]}}
        )

        # 2. Platform Users
        self.root_user, _ = PlatformUser.objects.get_or_create(
            username="root_admin",
            defaults={
                "email": "root@axinix.com",
                "role": self.role_root,
                "first_name": "Root",
                "last_name": "Admin",
            }
        )
        self.root_user.set_password("RootAdminPassword123!")
        self.root_user.save()
        self.root_user.plane = "platform"
        self.root_user.is_root_admin = True
        self.root_user.is_superadmin = False

        self.viewer_user, _ = PlatformUser.objects.get_or_create(
            username="management_viewer",
            defaults={
                "email": "viewer@axinix.com",
                "role": self.role_viewer,
                "first_name": "Executive",
                "last_name": "Viewer",
            }
        )
        self.viewer_user.set_password("ViewerPassword123!")
        self.viewer_user.save()
        self.viewer_user.plane = "platform"
        self.viewer_user.is_root_admin = False
        self.viewer_user.is_superadmin = False

        # 3. Client Tenant (Acme Corp)
        self.tenant, _ = Tenant.objects.get_or_create(
            tenant_id="acme-corp",
            defaults={
                "name": "Acme Corporation",
                "subdomain": "acme",
                "database_name": "tracker_acme",
                "plan": "Standard",
                "status": "Active",
                "enabled_modules": ["attendance"],
            }
        )
        self.tenant.enabled_modules = ["attendance"]
        self.tenant.save()

        # 4. Client Roles & Users
        self.client_role_super, _ = Role.objects.get_or_create(
            name="SuperAdmin", defaults={"is_superadmin": True, "status": 1}
        )
        self.client_admin, _ = User.objects.get_or_create(
            username="alice@acme.com",
            defaults={
                "email": "alice@acme.com",
                "role": self.client_role_super,
                "is_superuser": False,
                "is_staff": False,
            }
        )
        self.client_admin.role = self.client_role_super
        self.client_admin.save()
        self.client_admin.plane = "client"
        self.client_admin.is_root_admin = False
        self.client_admin.is_super_admin = True
        self.client_admin.tenant_id = "acme-corp"

        self.client = APIClient()

    def test_01_platform_root_admin_has_full_control(self):
        """Platform Root Admin has full global bypass on platform operations."""
        self.client.force_authenticate(user=self.root_user)
        res_tenant = self.client.get("/api/populate/read/tenant")
        self.assertEqual(res_tenant.status_code, 200)

        res_module = self.client.get("/api/populate/read/module")
        self.assertEqual(res_module.status_code, 200)

    def test_02_platform_management_viewer_is_read_only(self):
        """Platform Management Viewer can read tenants, but cannot create or mutate."""
        self.client.force_authenticate(user=self.viewer_user)

        # Read allowed
        res_read = self.client.get("/api/populate/read/tenant")
        self.assertEqual(res_read.status_code, 200)

        # Mutate blocked with 403 READ_ONLY_ROLE
        res_mutate = self.client.post("/api/populate/create/tenant", {
            "tenant_id": "unauth-tenant",
            "name": "Unauthorized Corp",
            "subdomain": "unauth-tenant",
            "database_name": "tracker_unauth"
        }, format="json")
        self.assertEqual(res_mutate.status_code, 403)
        self.assertEqual(res_mutate.data.get("error", {}).get("code"), "READ_ONLY_ROLE")

    def test_03_client_superadmin_blocked_from_platform_models(self):
        """
        Client SuperAdmin can inspect the public module catalog via Populate (200),
        but CANNOT mutate modules (403) and CANNOT access private platform models like tenant (403).
        """
        self.client.force_authenticate(user=self.client_admin)
        headers = {"HTTP_X_TENANT_ID": "acme-corp", "HTTP_X_TENANT_SLUG": "acme"}

        # 1. Module Catalog Read is open via Populate (for client and website)
        res_read_module = self.client.get("/api/populate/read/module", **headers)
        self.assertEqual(res_read_module.status_code, 200)

        # 2. Mutating modules is strictly blocked
        res_mutate_module = self.client.post("/api/populate/create/module", {"module_id": "hacked", "name": "Hacked Module"}, format="json", **headers)
        self.assertEqual(res_mutate_module.status_code, 403)
        self.assertEqual(res_mutate_module.data.get("error", {}).get("code"), "PLATFORM_ACCESS_FORBIDDEN")

        # 3. Private Platform Models (tenant, provisioning_run) are strictly blocked
        res_tenant = self.client.get("/api/populate/read/tenant", **headers)
        self.assertEqual(res_tenant.status_code, 403)
        self.assertEqual(res_tenant.data.get("error", {}).get("code"), "PLATFORM_ACCESS_FORBIDDEN")

    def test_04_initial_purchase_zero_permission_leakage(self):
        """
        When tenant buys only 'attendance':
        Attendance & Core are accessible (200),
        Payroll, CRM, Billing, Assets are strictly blocked (403).
        """
        self.client.force_authenticate(user=self.client_admin)
        headers = {"HTTP_X_TENANT_ID": "acme-corp", "HTTP_X_TENANT_SLUG": "acme"}

        # Attendance Allowed
        self.assertEqual(self.client.get("/api/populate/read/leave_type", **headers).status_code, 200)
        self.assertEqual(self.client.get("/api/populate/read/holiday_override", **headers).status_code, 200)

        # Core Allowed
        self.assertEqual(self.client.get("/api/populate/read/user", **headers).status_code, 200)
        self.assertEqual(self.client.get("/api/populate/read/role", **headers).status_code, 200)

        # Unsubscribed Modules Blocked with 403 MODULE_NOT_SUBSCRIBED
        for model in ["salary_structure", "expense", "opportunity", "quotation", "asset"]:
            res = self.client.get(f"/api/populate/read/{model}", **headers)
            self.assertEqual(res.status_code, 403, f"Model {model} leaked with status {res.status_code}!")
            self.assertEqual(res.data.get("error", {}).get("code"), "MODULE_NOT_SUBSCRIBED")

    def test_05_upgrade_activates_payroll_cleanly(self):
        """Upgrading tenant to ['attendance', 'payroll'] unlocks payroll immediately."""
        self.tenant.enabled_modules = ["attendance", "payroll"]
        self.tenant.save()

        self.client.force_authenticate(user=self.client_admin)
        headers = {"HTTP_X_TENANT_ID": "acme-corp", "HTTP_X_TENANT_SLUG": "acme"}

        # Attendance still works
        self.assertEqual(self.client.get("/api/populate/read/leave_type", **headers).status_code, 200)

        # Payroll now unlocked
        self.assertEqual(self.client.get("/api/populate/read/salary_structure", **headers).status_code, 200)

        # CRM still blocked
        res_crm = self.client.get("/api/populate/read/opportunity", **headers)
        self.assertEqual(res_crm.status_code, 403)
        self.assertEqual(res_crm.data.get("error", {}).get("code"), "MODULE_NOT_SUBSCRIBED")

    def test_06_degrade_revokes_payroll_with_zero_retention_leakage(self):
        """Downgrading tenant to ['attendance'] revokes payroll immediately."""
        self.tenant.enabled_modules = ["attendance"]
        self.tenant.save()

        self.client.force_authenticate(user=self.client_admin)
        headers = {"HTTP_X_TENANT_ID": "acme-corp", "HTTP_X_TENANT_SLUG": "acme"}

        # Attendance still works
        self.assertEqual(self.client.get("/api/populate/read/leave_type", **headers).status_code, 200)

        # Payroll is revoked
        res_payroll = self.client.get("/api/populate/read/salary_structure", **headers)
        self.assertEqual(res_payroll.status_code, 403)
        self.assertEqual(res_payroll.data.get("error", {}).get("code"), "MODULE_NOT_SUBSCRIBED")
