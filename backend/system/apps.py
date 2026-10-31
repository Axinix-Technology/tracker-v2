from django.apps import AppConfig


class SystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'system'
    verbose_name = 'System Telemetry & Platform Configuration'

    def ready(self):
        try:
            import system.services  # noqa: F401
        except ImportError:
            pass

