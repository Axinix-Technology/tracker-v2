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
        user_full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        # Resolve tenant ID & tenant slug
        from control_plane.models import UserLogin, Tenant
        user_login = UserLogin.objects.filter(email__iexact=user.email).select_related("tenant").first()
        tenant = user_login.tenant if user_login and user_login.tenant else None
        if not tenant:
            tenant = Tenant.objects.filter(tenant_id="axinix").first() or Tenant.objects.first()

        tenant_id = tenant.tenant_id if tenant else "axinix"
        tenant_slug = tenant.subdomain if tenant and tenant.subdomain else "axinix"

        jwt_payload = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user_full_name,
            "role": role_name,
            "roleId": user.role.id if user.role else None,
            "isSuperAdmin": is_super,
            "is_superadmin": is_super,
            "userType": "superadmin" if is_super else "employee",
            "firstName": user.first_name,
            "lastName": user.last_name,
            "tenantSlug": tenant_slug,
            "tenantId": tenant_id,
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
            "name": user_full_name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "role": role_data,
            "is_superadmin": is_super,
            "isSuperAdmin": is_super,
            "tenantId": tenant_id,
            "tenantSlug": tenant_slug,
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
    Returns user profile, role, permissions map, capabilities, and navigation.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role_obj = user.role
        role_name = role_obj.name if role_obj else "SuperAdmin"
        is_super = bool(
            getattr(user, "is_superadmin", False)
            or getattr(user, "is_superuser", False)
            or (role_obj and getattr(role_obj, "is_superadmin", False))
        )

        # Resolve tenant & enabled_modules
        from control_plane.models import UserLogin, Tenant
        user_login = UserLogin.objects.filter(email__iexact=user.email).select_related("tenant").first()
        tenant = user_login.tenant if user_login and user_login.tenant else None
        if not tenant:
            tenant = Tenant.objects.filter(tenant_id="axinix").first() or Tenant.objects.first()

        enabled_modules = tenant.enabled_modules if tenant and tenant.enabled_modules else []
        tenant_id = tenant.tenant_id if tenant else "axinix"
        tenant_slug = tenant.subdomain if tenant and tenant.subdomain else "axinix"

        from populate_core.registry.model_registry import ModelRegistry
        from control_plane.registry import is_model_entitled, is_platform_model

        permissions = {}
        for m_name in ModelRegistry.get_all().keys():
            # Exclude private platform models from client user context
            if is_platform_model(m_name) and m_name not in ("module", "modules"):
                continue

            entitled = is_model_entitled(m_name, enabled_modules)
            permissions[m_name] = {
                "read": entitled,
                "create": is_super and entitled,
                "update": is_super and entitled,
                "delete": is_super and entitled,
                "report": entitled,
                "isEntitled": entitled,
            }

        user_full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        from users.navigation import get_user_navigation
        nav_tree = get_user_navigation(user, enabled_modules=enabled_modules, is_superadmin=is_super)

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
                    },
                    "tenantId": tenant_id,
                    "tenantSlug": tenant_slug,
                },
                "tenantId": tenant_id,
                "tenantSlug": tenant_slug,
                "enabled_modules": enabled_modules,
                "capabilities": [],
                "permissions": permissions,
                "navigation": nav_tree,
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
