from django.apps import AppConfig


class FeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feed'

    def ready(self):
        try:
            import feed.services  # noqa: F401
        except ImportError:
            pass
