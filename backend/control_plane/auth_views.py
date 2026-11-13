import datetime
import jwt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import PlatformUser, PlatformRole


class PlatformLoginView(APIView):
    """
    Dedicated Platform Plane Authentication Endpoint.
    Authenticates Platform Staff (Root Admins, Management Viewers, Support Engineers).
    Generates signed platform JWT containing plane='platform'.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"success": False, "error": "Username/email and password required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        platform_user = PlatformUser.objects.select_related("role").filter(
            username__iexact=username
        ).first() or PlatformUser.objects.select_related("role").filter(
            email__iexact=username
        ).first()

        if not platform_user or not platform_user.check_password(password):
            return Response(
                {"success": False, "error": "Invalid platform credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not platform_user.is_active:
            return Response(
                {"success": False, "error": "Platform account is inactive or suspended."},
                status=status.HTTP_403_FORBIDDEN
            )

        role = platform_user.role
        is_root = bool(role.is_root_admin)

        jwt_payload = {
            "id": platform_user.id,
            "username": platform_user.username,
            "email": platform_user.email,
            "plane": "platform",
            "userType": "platform_admin",
            "role": role.role_id,
            "roleName": role.name,
            "isRootAdmin": is_root,
            "is_root_admin": is_root,
            "isSuperAdmin": False,  # Not a client superadmin
            "permissions": role.permissions,
            "firstName": platform_user.first_name,
            "lastName": platform_user.last_name,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
            "iat": datetime.datetime.now(datetime.timezone.utc),
        }

        jwt_secret = getattr(settings, "SECRET_KEY", "django-insecure-tracker-v2-axinix-core-dev-key")
        access_token = jwt.encode(jwt_payload, jwt_secret, algorithm="HS256")
        refresh_token = jwt.encode(
            {"id": platform_user.id, "plane": "platform", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)},
            jwt_secret,
            algorithm="HS256"
        )

        # Update last login
        platform_user.last_login = datetime.datetime.now(datetime.timezone.utc)
        platform_user.save(update_fields=["last_login"])

        return Response({
            "success": True,
            "message": "Platform authentication successful.",
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "data": {
                "accessToken": access_token,
                "user": {
                    "id": platform_user.id,
                    "username": platform_user.username,
                    "email": platform_user.email,
                    "firstName": platform_user.first_name,
                    "lastName": platform_user.last_name,
                    "role": {
                        "id": role.id,
                        "roleId": role.role_id,
                        "name": role.name,
                        "isRootAdmin": is_root,
                        "permissions": role.permissions,
                    },
                    "plane": "platform",
                }
            }
        })


class PlatformContextView(APIView):
    """
    GET /api/platform/auth/me/context
    Returns platform user profile, role, and platform capabilities.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, "plane", None) != "platform":
            return Response(
                {"success": False, "error": "Endpoint restricted to Platform Operators."},
                status=status.HTTP_403_FORBIDDEN
            )

        role = getattr(user, "role", None)
        return Response({
            "success": True,
            "data": {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                    "plane": "platform",
                    "role": {
                        "id": role.id if role else 1,
                        "roleId": getattr(role, "role_id", "root_admin"),
                        "name": getattr(role, "name", "Platform Root Admin"),
                        "isRootAdmin": getattr(role, "is_root_admin", False),
                        "permissions": getattr(role, "permissions", {}),
                    }
                }
            }
        })

