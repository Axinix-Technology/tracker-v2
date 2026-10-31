from django.urls import path
from .views import LoginView, ProfileView, UserContextView, LogoutView, ChangePasswordView

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('login', LoginView.as_view(), name='auth-login-no-slash'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('logout', LogoutView.as_view(), name='auth-logout-no-slash'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('change-password', ChangePasswordView.as_view(), name='auth-change-password-no-slash'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('me', ProfileView.as_view(), name='auth-me-no-slash'),
    path('me/', ProfileView.as_view(), name='auth-me'),
    path('me/context', UserContextView.as_view(), name='auth-me-context-no-slash'),
    path('me/context/', UserContextView.as_view(), name='auth-me-context'),
]
