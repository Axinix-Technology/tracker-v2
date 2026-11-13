import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.authtoken.models import Token

User = get_user_model()

class DualTokenAndBearerAuthentication(BaseAuthentication):
    """
    Seamless Dual Authentication supporting:
    1. 'Authorization: Bearer <jwt_or_key>' (standard for React / Axios frontend)
    2. 'Authorization: Token <key>' (standard for DRF / cURL clients)
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth:
            return None

        prefix = auth[0].lower().decode("utf-8")
        if prefix not in ("bearer", "token"):
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed("Invalid authorization header. No token provided.")
        elif len(auth) > 2:
            raise exceptions.AuthenticationFailed("Invalid authorization header. Token string should not contain spaces.")

        token_str = auth[1].decode("utf-8")

        # 1. First, attempt decoding as signed JWT
        try:
            jwt_secret = getattr(settings, "SECRET_KEY", "django-insecure-tracker-v2-axinix-core-dev-key")
            payload = jwt.decode(token_str, jwt_secret, algorithms=["HS256"])
            user_id = payload.get("id") or payload.get("user_id")
            plane = payload.get("plane", "client")

            # Platform Plane User Resolution
            if plane == "platform":
                from control_plane.models import PlatformUser
                platform_user = PlatformUser.objects.select_related("role").filter(pk=user_id).first()
                if platform_user and platform_user.is_active:
                    platform_user.plane = "platform"
                    platform_user.is_root_admin = getattr(platform_user.role, "is_root_admin", False)
                    platform_user.is_superadmin = False
                    platform_user.is_superuser = platform_user.is_root_admin
                    return (platform_user, token_str)

            # Client Plane User Resolution
            if user_id:
                user = User.objects.select_related("role").filter(pk=user_id).first()
                if user and user.is_active:
                    user.plane = "client"
                    user.is_root_admin = False
                    user.is_super_admin = getattr(getattr(user, "role", None), "is_superadmin", False)
                    # Resolve tenant ID from token, header, or query
                    tenant_id = (
                        payload.get("tenant_id")
                        or payload.get("tenantSlug")
                        or (request.headers.get("X-Tenant-ID") if hasattr(request, "headers") else None)
                        or request.META.get("HTTP_X_TENANT_ID")
                        or "default"
                    )
                    user.tenant_id = tenant_id
                    return (user, token_str)
        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
            pass

        # 2. Second, attempt matching as DRF Database Token
        try:
            token_obj = Token.objects.select_related("user").get(key=token_str)
            if not token_obj.user.is_active:
                raise exceptions.AuthenticationFailed("User inactive or deleted.")
            token_obj.user.plane = "client"
            token_obj.user.is_root_admin = False
            token_obj.user.is_super_admin = getattr(getattr(token_obj.user, "role", None), "is_superadmin", False)
            token_obj.user.tenant_id = (
                (request.headers.get("X-Tenant-ID") if hasattr(request, "headers") else None)
                or request.META.get("HTTP_X_TENANT_ID")
                or "default"
            )
            return (token_obj.user, token_obj)
        except Token.DoesNotExist:
            pass

        raise exceptions.AuthenticationFailed("Invalid or expired token.")

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
