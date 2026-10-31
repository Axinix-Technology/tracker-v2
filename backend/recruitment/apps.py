from django.apps import AppConfig


class RecruitmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recruitment'
    verbose_name = 'Recruitment & Employee Onboarding'

    def ready(self):
        try:
            import recruitment.services  # noqa: F401
        except ImportError:
            pass

