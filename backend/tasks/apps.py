from django.apps import AppConfig

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        try:
            import tasks.services  # noqa: F401
        except ImportError:
            pass
