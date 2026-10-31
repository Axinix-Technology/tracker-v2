from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from populate_core.registry import register_model

@register_model("role", table_type="master")
class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_superadmin = models.BooleanField(default=False, db_index=True)
    permission_version = models.PositiveIntegerField(default=1)
    status = models.SmallIntegerField(default=1, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.name


@register_model("department", table_type="master")
class Department(models.Model):
    name = models.CharField(max_length=128, unique=True)
    short_code = models.CharField(max_length=32, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "departments"

    def __str__(self):
        return self.name


@register_model("designation", table_type="master")
class Designation(models.Model):
    title = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "designations"

    def __str__(self):
        return self.title


@register_model("company", table_type="master")
class Company(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "companies"

    def __str__(self):
        return self.name


@register_model("client", table_type="master", aliases=["clients"])
class Client(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner_name = models.CharField(max_length=255, blank=True, null=True)
    business_type = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "clients"

    def __str__(self):
        return self.name


@register_model("project_type", table_type="master", aliases=["project_types", "projecttypes"])
class ProjectType(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_types"

    def __str__(self):
        return self.name


@register_model("user", table_type="master", aliases=["employee", "employees"])
class User(AbstractUser):
    emp_id = models.CharField(max_length=64, unique=True, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    reporting_manager = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subordinates")
    team_lead = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="team_members")
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.CharField(max_length=512, blank=True, null=True)
    gender = models.CharField(max_length=16, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    doj = models.DateField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username

    @property
    def is_superadmin(self):
        if self.is_superuser:
            return True
        if self.role and getattr(self.role, "is_superadmin", False):
            return True
        return False


class BasicInfo(models.Model):
    """
    Sub-entity representing employee basic info.
    Resolves dot-notation queries like 'basicInfo.firstName' from Frontend.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="basicInfo")
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.CharField(max_length=512, blank=True, null=True)
    gender = models.CharField(max_length=16, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employee_basic_info"

    def __str__(self):
        return f"BasicInfo for {self.user}"

    @property
    def firstName(self):
        return self.first_name

    @property
    def lastName(self):
        return self.last_name

    @property
    def profileImage(self):
        return self.profile_image


class ProfessionalInfo(models.Model):
    """
    Sub-entity representing employee professional info.
    Resolves dot-notation queries like 'professionalInfo.department' and 'professionalInfo.designation'.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="professionalInfo")
    emp_id = models.CharField(max_length=64, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="professional_infos")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="professional_infos")
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True, related_name="professional_infos")
    reporting_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_professional_infos")
    team_lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="lead_professional_infos")
    level = models.CharField(max_length=16, blank=True, null=True)
    doj = models.DateField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employee_professional_info"

    def __str__(self):
        return f"ProfessionalInfo for {self.user}"

    @property
    def empId(self):
        return self.emp_id


@receiver(post_save, sender=User)
def sync_user_sub_info(sender, instance, created, **kwargs):
    """
    Keep BasicInfo and ProfessionalInfo in sync with User model.
    """
    BasicInfo.objects.update_or_create(
        user=instance,
        defaults={
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": instance.email,
            "phone": instance.phone,
            "profile_image": instance.profile_image,
            "gender": instance.gender,
            "dob": instance.dob,
            "status": instance.status,
        }
    )
    ProfessionalInfo.objects.update_or_create(
        user=instance,
        defaults={
            "emp_id": instance.emp_id,
            "role": instance.role,
            "department": instance.department,
            "designation": instance.designation,
            "reporting_manager": instance.reporting_manager,
            "team_lead": instance.team_lead,
            "doj": instance.doj,
            "status": instance.status,
        }
    )
