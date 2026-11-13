import datetime
# pyrefly: ignore[missing-import]
import jwt
# pyrefly: ignore[missing-import]
from django.conf import settings
# pyrefly: ignore[missing-import]
from django.contrib.auth import authenticate
# pyrefly: ignore[missing-import]
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = (
            request.data.get("username")
            or request.data.get("workEmail")
            or request.data.get("email")
        )
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"success": False, "error": "Username and password required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Allow login by email or username
        user = authenticate(username=username, password=password)
        if not user:
            # Try finding user by email first
            from .models import User
            matched_user = User.objects.filter(email__iexact=username).first()
            if matched_user and matched_user.check_password(password):
                user = matched_user

        if not user:
            return Response(
                {"success": False, "error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        drf_token, _ = Token.objects.get_or_create(user=user)

        role_name = user.role.name if user.role else "Employee"
        is_super = bool(
            (user.role and getattr(user.role, "is_superadmin", False))
            or getattr(user, "is_superuser", False)
            or getattr(user, "is_superadmin", False)
        )

        # Construct JWT payload matching Frontend jwtDecode expectations
        jwt_payload = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": role_name,
            "roleId": user.role.id if user.role else None,
            "isSuperAdmin": is_super,
            "is_superadmin": is_super,
            "userType": "superadmin" if is_super else "employee",
            "firstName": user.first_name,
            "lastName": user.last_name,
            "tenantSlug": "admin",
            "tenantId": "default",
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
            "iat": datetime.datetime.now(datetime.timezone.utc),
        }

        jwt_secret = getattr(settings, "SECRET_KEY", "axinix-secret-dev-key")
        access_token = jwt.encode(jwt_payload, jwt_secret, algorithm="HS256")
        refresh_token = jwt.encode(
            {"id": user.id, "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)},
            jwt_secret,
            algorithm="HS256"
        )

        role_data = None
        if user.role:
            role_data = {
                "id": user.role.id,
                "name": user.role.name,
                "is_superadmin": user.role.is_superadmin,
            }

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": role_data,
            "is_superadmin": is_super,
            "isSuperAdmin": is_super,
        }

        # Dual envelope: works for both React Frontend and DRF clients
        return Response({
            "success": True,
            "message": "Login successful",
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "token": drf_token.key,
            "data": {
                "token": drf_token.key,
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "user": user_data,
            }
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role_data = {
            "id": user.role.id,
            "name": user.role.name,
            "is_superadmin": user.role.is_superadmin
        } if user.role else None

        return Response({
            "success": True,
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": role_data,
                "is_superadmin": user.is_superadmin,
            }
        })


class UserContextView(APIView):
    """
    GET /api/auth/me/context
    Returns user profile, role, permissions map, and capabilities.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role_obj = user.role
        role_name = role_obj.name if role_obj else "SuperAdmin"
        is_super = getattr(user, "is_superadmin", False)

        from populate_core.registry.model_registry import ModelRegistry
        permissions = {}
        for m_name in ModelRegistry.get_all().keys():
            permissions[m_name] = {
                "read": True,
                "create": is_super,
                "update": is_super,
                "delete": is_super,
                "report": True,
            }

        user_full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        return Response({
            "success": True,
            "data": {
                "user": {
                    "id": user.id,
                    "name": user_full_name,
                    "email": user.email,
                    "profileImage": user.profile_image,
                    "empId": user.emp_id or "EMP001",
                    "department": user.department.name if user.department else None,
                    "designation": user.designation.title if user.designation else None,
                    "role": {
                        "id": role_obj.id if role_obj else 1,
                        "name": role_name,
                        "level": 1,
                        "isSuperAdmin": is_super,
                    }
                },
                "capabilities": [],
                "permissions": permissions,
                "navigation": [],
                "_v": 1,
                "_cachedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
        })


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response({
            "success": True,
            "message": "Logged out successfully"
        })


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("currentPassword") or request.data.get("oldPassword")
        new_password = request.data.get("newPassword")

        if not current_password or not new_password:
            return Response(
                {"success": False, "error": "Both current and new password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.check_password(current_password):
            return Response(
                {"success": False, "error": "Current password does not match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.set_password(new_password)
        request.user.save(update_fields=["password"])

        return Response({
            "success": True,
            "message": "Password changed successfully."
        })
