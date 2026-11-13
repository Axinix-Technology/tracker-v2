from django.apps import AppConfig


class ControlPlaneConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'control_plane'
    verbose_name = 'Multi-Tenant Control Plane'

    def ready(self):
        try:
            import control_plane.services  # noqa: F401
            from control_plane.policy_patch import apply_policy_patch
            apply_policy_patch()
        except Exception as exc:
            import traceback
            traceback.print_exc()

