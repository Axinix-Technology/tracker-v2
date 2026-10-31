from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billing'
    verbose_name = 'Client Invoicing & Accounting'

    def ready(self):
        try:
            import billing.services  # noqa: F401
        except ImportError:
            pass

