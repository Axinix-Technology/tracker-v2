from django.apps import AppConfig


class ControlPlaneConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'control_plane'
    verbose_name = 'Multi-Tenant Control Plane'

    def ready(self):
        try:
            import control_plane.services  # noqa: F401
        except ImportError:
            pass

