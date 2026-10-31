from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import Role

User = get_user_model()


class UserSecurityTestCase(TestCase):
    def setUp(self):
        self.role_super, _ = Role.objects.get_or_create(
            name="SuperAdmin", defaults={"is_superadmin": True, "status": 1}
        )
        self.role_emp, _ = Role.objects.get_or_create(
            name="Employee", defaults={"is_superadmin": False, "status": 1}
        )

        self.admin = User.objects.create_user(
            username="super_admin",
            email="admin@example.com",
            password="AdminPassword123!",
            is_superuser=True,
            is_staff=True,
            role=self.role_super
        )

        self.alice = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="AlicePassword123!",
            role=self.role_emp
        )

        self.bob = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="BobPassword123!",
            role=self.role_emp
        )

        self.client = APIClient()

    def test_admin_can_create_user_with_hashed_password(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(
            "/api/populate/create/user/",
            {
                "username": "new_hire",
                "email": "newhire@example.com",
                "password": "SecureHirePass123!",
                "first_name": "New",
                "last_name": "Hire",
                "role": self.role_emp.id,
            },
            format="json"
        )
        self.assertEqual(res.status_code, 201)
        created_user = User.objects.get(username="new_hire")
        self.assertTrue(created_user.check_password("SecureHirePass123!"))
        # Verify plaintext is not stored
        self.assertNotEqual(created_user.password, "SecureHirePass123!")

    def test_non_superadmin_cannot_create_user(self):
        self.client.force_authenticate(user=self.alice)
        res = self.client.post(
            "/api/populate/create/user/",
            {
                "username": "hacker_user",
                "email": "hacker@example.com",
                "password": "Password123!",
            },
            format="json"
        )
        self.assertIn(res.status_code, (400, 403))

    def test_non_superadmin_cannot_update_user(self):
        self.client.force_authenticate(user=self.alice)
        res = self.client.post(
            f"/api/populate/update/user/{self.alice.id}/",
            {
                "is_superuser": True,
                "is_staff": True,
                "role": self.role_super.id,
            },
            format="json"
        )
        self.assertIn(res.status_code, (400, 403))
        self.alice.refresh_from_db()
        self.assertFalse(self.alice.is_superuser)
        self.assertFalse(self.alice.is_staff)
        self.assertEqual(self.alice.role.id, self.role_emp.id)

    def test_admin_can_update_user_and_hash_password(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(
            f"/api/populate/update/user/{self.alice.id}/",
            {
                "first_name": "AliceUpdatedByAdmin",
                "password": "NewAlicePassword456!",
            },
            format="json"
        )
        self.assertEqual(res.status_code, 200)
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.first_name, "AliceUpdatedByAdmin")
        self.assertTrue(self.alice.check_password("NewAlicePassword456!"))

    def test_password_is_forbidden_in_read_projection(self):
        self.client.force_authenticate(user=self.alice)
        res = self.client.post(
            "/api/populate/read/user/",
            {"filter": {"id": self.alice.id}},
            format="json"
        )
        self.assertEqual(res.status_code, 200)
        user_data = res.data["data"]
        item = user_data[0] if isinstance(user_data, list) else user_data
        self.assertNotIn("password", item)
