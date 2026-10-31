from django.db import models
from populate_core.registry import register_model

@register_model("dashboard_schema", table_type="master", aliases=["dashboard_schemas", "dashboardschema"])
class DashboardSchema(models.Model):
    role = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=128, default="Role Dashboard Layout")
    version = models.PositiveIntegerField(default=1)
    layout = models.JSONField(default=dict)
    widgets = models.JSONField(default=list)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dashboard_schemas"

    def __str__(self):
        return f"{self.role} Dashboard (v{self.version})"


@register_model("dashboard_widget", table_type="master", aliases=["dashboard_widgets", "dashboardwidget"])
class DashboardWidget(models.Model):
    role = models.OneToOneField("users.Role", on_delete=models.CASCADE, related_name="dashboard_widgets")
    widgets = models.JSONField(default=list)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dashboard_widgets"

    def __str__(self):
        return f"Widgets for {self.role}"
