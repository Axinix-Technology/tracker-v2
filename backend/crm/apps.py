from django.apps import AppConfig


class CRMConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    verbose_name = 'Customer Relationship Management'

    def ready(self):
        try:
            import crm.services  # noqa: F401
        except ImportError:
            pass

