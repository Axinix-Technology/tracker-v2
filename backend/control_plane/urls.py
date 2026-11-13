from django.urls import path
from .auth_views import PlatformLoginView, PlatformContextView

urlpatterns = [
    path('auth/login/', PlatformLoginView.as_view(), name='platform-auth-login'),
    path('auth/login', PlatformLoginView.as_view(), name='platform-auth-login-no-slash'),
    path('auth/me/context/', PlatformContextView.as_view(), name='platform-auth-context'),
    path('auth/me/context', PlatformContextView.as_view(), name='platform-auth-context-no-slash'),
]

