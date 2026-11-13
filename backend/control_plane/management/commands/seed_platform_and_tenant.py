import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from control_plane.models import Tenant, UserLogin, Module, PlatformRole, PlatformUser
from control_plane.registry import CLIENT_BUSINESS_MODULES

User = get_user_model()

ALL_MODULE_IDS = [
    "attendance",
    "payroll",
    "crm",
    "billing",
    "tasks",
    "tickets",
    "assets",
    "recruitment",
    "hr",
    "feed",
    "contributions",
]

class Command(BaseCommand):
    help = "Seeds the Platform Admin in Control Plane and the default Customer Plane Tenant for Axinix with all modules enabled"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("===> 1. Seeding Platform Role: Root Admin..."))
        root_role, _ = PlatformRole.objects.update_or_create(
            role_id="root_admin",
            defaults={
                "name": "Root Administrator",
                "description": "Full Control Plane platform root supervisor with omnipotent permissions across all organizations and tenants.",
                "is_root_admin": True,
                "permissions": {"*": ["*"]},
                "is_active": True,
                "lifecycle_status": 1,
            }
        )
        self.stdout.write(self.style.SUCCESS(f"  ✓ Platform Role verified: {root_role}"))

        self.stdout.write(self.style.NOTICE("===> 2. Seeding Platform Admins..."))
        # Primary platform admin: admin@axinix.com / admin
        admin_user, created = PlatformUser.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@axinix.com",
                "first_name": "Platform",
                "last_name": "Administrator",
                "role": root_role,
                "is_active": True,
                "lifecycle_status": 1,
            }
        )
        admin_user.set_password("Admin@123")
        admin_user.role = root_role
        admin_user.email = "admin@axinix.com"
        admin_user.is_active = True
        admin_user.save()

        # Secondary platform admin: root_admin@controlplane.com
        root_control, _ = PlatformUser.objects.get_or_create(
            username="root_admin",
            defaults={
                "email": "root_admin@controlplane.com",
                "first_name": "Root",
                "last_name": "Supervisor",
                "role": root_role,
                "is_active": True,
                "lifecycle_status": 1,
            }
        )
        root_control.set_password("Admin@123")
        root_control.role = root_role
        root_control.is_active = True
        root_control.save()

        self.stdout.write(self.style.SUCCESS("  ✓ Platform Admins created with password 'Admin@123'."))

        self.stdout.write(self.style.NOTICE("===> 3. Seeding Customer Plane Tenant for Axinix (All Modules Enabled)..."))
        axinix_tenant, _ = Tenant.objects.update_or_create(
            tenant_id="axinix",
            defaults={
                "name": "Axinix Technologies",
                "subdomain": "axinix",
                "database_name": "workhub_db",
                "plan": "Enterprise",
                "status": "Active",
                "enabled_modules": ALL_MODULE_IDS,
                "settings": {
                    "is_default": True,
                    "currency": "INR",
                    "timezone": "Asia/Kolkata",
                    "all_modules_entitled": True,
                    "company_name": "Axinix Technologies",
                },
                "lifecycle_status": 1,
            }
        )
        self.stdout.write(self.style.SUCCESS(f"  ✓ Axinix Tenant configured: {axinix_tenant.name} [{axinix_tenant.tenant_id}]"))
        self.stdout.write(f"    Enabled Modules ({len(axinix_tenant.enabled_modules)}): {', '.join(axinix_tenant.enabled_modules)}")

        self.stdout.write(self.style.NOTICE("===> 4. Syncing Client SuperAdmin & Team Users..."))
        from users.models import Role
        superadmin_role = Role.objects.filter(is_superadmin=True).first() or Role.objects.first()

        team_accounts = [
            ("arunbharathi", "arunbharathi@axinix.com", "Arunbharathi", True),
            ("admin", "admin@axinix.com", "Platform Admin", True),
            ("admin", "admin@tracker.com", "Platform Admin", True),
            ("ajay", "ajay@axinix.com", "Ajay", True),
            ("siva", "siva@axinix.com", "Siva Anna", True),
            ("rithika", "rithika@axinix.com", "Rithika", True),
            ("karuppasamy", "karuppasamy@axinix.com", "Karuppasamy", True),
            ("ruthran", "ruthran@axinix.com", "Ruthran", True),
            ("guruprasath", "guruprasath@axinix.com", "Guruprasath", True),
            ("boopalan", "boopalan@axinix.com", "Boopalan", True),
        ]

        for username, email, name, is_super in team_accounts:
            u = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=username).first()
            if not u:
                u = User.objects.create(
                    username=username,
                    email=email,
                    first_name=name,
                )
            u.email = email
            u.first_name = name
            u.set_password("Admin@123")
            if superadmin_role and is_super:
                u.role = superadmin_role
            u.is_staff = is_super
            u.is_superuser = is_super
            u.is_active = True
            u.save()

            UserLogin.objects.update_or_create(
                email=email,
                tenant=axinix_tenant,
                defaults={
                    "user_id": u.id,
                    "is_superadmin": is_super,
                    "is_active": True,
                    "lifecycle_status": 1,
                }
            )

        self.stdout.write(self.style.SUCCESS("  ✓ Centralized UserLogins & Passwords set for all team members (Password: Admin@123)."))
        self.stdout.write(self.style.SUCCESS("\n🎉 Platform Admin & Axinix Default Tenant Seed Completed Successfully!"))
