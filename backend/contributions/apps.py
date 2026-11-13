from django.apps import AppConfig

class ContributionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contributions'

    def ready(self):
        try:
            import contributions.services  # noqa: F401
        except ImportError:
            pass

