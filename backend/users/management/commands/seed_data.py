from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from users.models import Role, Department, Designation, Company

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds initial roles, departments, companies, and admin/employee users into MySQL"

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        # 1. Roles
        super_role, _ = Role.objects.get_or_create(
            name="SuperAdmin",
            defaults={"description": "Full System Administrator", "is_superadmin": True, "status": 1}
        )
        if not super_role.is_superadmin:
            super_role.is_superadmin = True
            super_role.save()

        emp_role, _ = Role.objects.get_or_create(
            name="Employee",
            defaults={"description": "Standard Employee", "is_superadmin": False, "status": 1}
        )

        # 2. Department & Designation & Company
        dept, _ = Department.objects.get_or_create(
            name="Engineering",
            defaults={"short_code": "ENG", "status": 1}
        )
        desig, _ = Designation.objects.get_or_create(
            title="Software Engineer",
            defaults={"status": 1}
        )
        company, _ = Company.objects.get_or_create(
            name="Axinix Technologies",
            defaults={"code": "AXN", "email": "info@axinix.com", "status": 1}
        )

        # 3. SuperAdmin User
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@axinix.com",
                "first_name": "Axinix",
                "last_name": "Admin",
                "emp_id": "EMP001",
                "role": super_role,
                "department": dept,
                "designation": desig,
                "company": company,
                "is_staff": True,
                "is_superuser": True,
                "status": 1,
            }
        )
        admin_user.set_password("admin123")
        admin_user.role = super_role
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        Token.objects.get_or_create(user=admin_user)
        self.stdout.write(self.style.SUCCESS(f"SuperAdmin ready: admin@axinix.com / admin123 (id={admin_user.id})"))

        # 4. Standard Employee User
        emp_user, created = User.objects.get_or_create(
            username="employee",
            defaults={
                "email": "employee@axinix.com",
                "first_name": "Test",
                "last_name": "Employee",
                "emp_id": "EMP002",
                "role": emp_role,
                "department": dept,
                "designation": desig,
                "company": company,
                "status": 1,
            }
        )
        emp_user.set_password("emp123")
        emp_user.role = emp_role
        emp_user.save()
        Token.objects.get_or_create(user=emp_user)
        self.stdout.write(self.style.SUCCESS(f"Employee ready: employee@axinix.com / emp123 (id={emp_user.id})"))

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
