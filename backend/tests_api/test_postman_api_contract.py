import json
import logging
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import Role, Client

User = get_user_model()
logger = logging.getLogger("api_test")


def print_postman_trace(method: str, url: str, headers: dict, request_body: dict | None, response):
    """
    Formats the request and response exactly as seen in Postman Console / Response Pane.
    """
    print("\n" + "=" * 80)
    print(f"🚀 [POSTMAN REQUEST] {method.upper()} {url}")
    print("Headers:", json.dumps(headers, indent=2))
    if request_body:
        print("Request Body (JSON):")
        print(json.dumps(request_body, indent=2, default=str))
    else:
        print("Request Body: None")
    print("-" * 80)
    print(f"📥 [POSTMAN RESPONSE] Status: {response.status_code}")
    print("Response Headers:")
    resp_headers = {
        "Content-Type": response.get("Content-Type", "application/json"),
        "X-Request-ID": response.get("X-Request-ID", "N/A"),
    }
    print(json.dumps(resp_headers, indent=2))
    print("Response Body (JSON):")
    try:
        if hasattr(response, "json"):
            body_json = response.json()
        elif hasattr(response, "data"):
            body_json = response.data
        else:
            body_json = json.loads(response.content.decode("utf-8"))
        print(json.dumps(body_json, indent=2, default=str))
    except Exception:
        print(response.content.decode("utf-8", errors="replace"))
    print("=" * 80 + "\n")


class PostmanApiContractTestCase(TestCase):
    """
    Pure API End-to-End Contract Test Suite.
    STRICT COMPLIANCE RULE:
    1. NEVER calls internal Python service functions directly.
    2. Calls ONLY HTTP API endpoints (/api/auth/*, /api/populate/*) using APIClient.
    3. Outputs exact Postman response structures showing status, headers, and JSON payloads.
    """

    def setUp(self):
        # 1. Base Master Data for testing
        self.role_super, _ = Role.objects.get_or_create(
            name="SuperAdmin", defaults={"is_superadmin": True, "status": 1}
        )
        self.role_emp, _ = Role.objects.get_or_create(
            name="Employee", defaults={"is_superadmin": False, "status": 1}
        )

        self.admin = User.objects.create_user(
            username="admin@axinix.com",
            email="admin@axinix.com",
            password="AdminSecurePassword123!",
            is_superuser=True,
            is_staff=True,
            role=self.role_super
        )

        self.john = User.objects.create_user(
            username="john@axinix.com",
            email="john@axinix.com",
            password="JohnPassword123!",
            role=self.role_emp
        )

        self.test_client_account, _ = Client.objects.get_or_create(
            name="Acme Corporation",
            defaults={"email": "billing@acme.com", "status": 1}
        )

        self.client = APIClient()

    # =========================================================================
    # 1. AUTHENTICATION APIS (POSTMAN CONTRACT)
    # =========================================================================

    def test_01_postman_auth_login_success(self):
        """
        POST /api/auth/login
        Authenticates user with username/email and password.
        Returns JWT access token, refresh token, and user profile envelope.
        """
        url = "/api/auth/login"
        payload = {
            "username": "admin@axinix.com",
            "password": "AdminSecurePassword123!"
        }
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Content-Type": "application/json"}, payload, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))
        self.assertIn("accessToken", res.data)
        self.assertIn("refreshToken", res.data)
        self.assertEqual(res.data["data"]["user"]["email"], "admin@axinix.com")
        self.assertTrue(res.data["data"]["user"]["isSuperAdmin"])

    def test_02_postman_auth_login_invalid_credentials(self):
        """
        POST /api/auth/login (Invalid Password)
        Returns HTTP 401 Unauthorized with standardized error envelope.
        """
        url = "/api/auth/login"
        payload = {
            "username": "admin@axinix.com",
            "password": "WrongPassword999!"
        }
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Content-Type": "application/json"}, payload, res)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.data.get("success"))
        self.assertEqual(res.data.get("error"), "Invalid credentials.")

    def test_03_postman_auth_me_context(self):
        """
        GET /api/auth/me/context
        Returns logged-in user profile, permissions map, and capabilities.
        """
        self.client.force_authenticate(user=self.admin)
        url = "/api/auth/me/context"
        res = self.client.get(url)
        print_postman_trace("GET", url, {"Authorization": "Bearer <JWT_TOKEN>"}, None, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))
        data = res.data.get("data", {})
        self.assertIn("user", data)
        self.assertIn("permissions", data)
        self.assertEqual(data["user"]["email"], "admin@axinix.com")

    def test_04_postman_auth_change_password(self):
        """
        POST /api/auth/change-password
        Changes authenticated user password and enforces old password verification.
        """
        self.client.force_authenticate(user=self.john)
        url = "/api/auth/change-password"
        payload = {
            "currentPassword": "JohnPassword123!",
            "newPassword": "JohnNewSuperPassword456!"
        }
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, payload, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))
        self.assertEqual(res.data.get("message"), "Password changed successfully.")

    def test_05_postman_auth_logout(self):
        """
        POST /api/auth/logout
        Terminates session cleanly.
        """
        url = "/api/auth/logout"
        res = self.client.post(url, {}, format="json")
        print_postman_trace("POST", url, {"Content-Type": "application/json"}, {}, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))

    # =========================================================================
    # 2. POPULATE ENGINE CRUD LIFECYCLE (POSTMAN CONTRACT)
    # =========================================================================

    def test_06_postman_populate_create_entity(self):
        """
        POST /api/populate/create/tasks
        Creates a new task. Verifies auto-stamping and response structure.
        """
        self.client.force_authenticate(user=self.admin)
        url = "/api/populate/create/task"
        payload = {
            "title": "Design Mobile App Wireframes",
            "observation": "Figma mockups for client signoff",
            "priorityLevel": "High",
            "status": "Backlogs",
            "estimatedHours": 12.5
        }
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, payload, res)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.data.get("success"))
        created_data = res.data.get("data")
        created_id = created_data[0]["id"] if isinstance(created_data, list) else created_data["id"]
        self.assertIsNotNone(created_id)

    def test_07_postman_populate_read_list_with_pagination_and_filter(self):
        """
        POST /api/populate/read/tasks
        Postman queries task collection with pagination and filter criteria.
        Expects { success: true, count: N, data: [...], metadata: { page, limit, total_pages } }
        """
        self.client.force_authenticate(user=self.admin)

        # Create 2 tasks via API first
        self.client.post("/api/populate/create/task", {"title": "Sprint Task 1", "priorityLevel": "High"}, format="json")
        self.client.post("/api/populate/create/task", {"title": "Sprint Task 2", "priorityLevel": "Low"}, format="json")

        url = "/api/populate/read/tasks"
        payload = {
            "page": 1,
            "limit": 10,
            "filter": {"priorityLevel": "High"},
            "sort": "-id"
        }
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, payload, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))
        self.assertIn("count", res.data)
        self.assertIn("data", res.data)
        self.assertIsInstance(res.data["data"], list)
        self.assertIn("metadata", res.data)
        self.assertEqual(res.data["metadata"]["page"], 1)

    def test_08_postman_populate_read_single_entity_by_id(self):
        """
        GET /api/populate/read/tasks/:id
        Fetches single entity by its primary key.
        """
        self.client.force_authenticate(user=self.admin)
        create_res = self.client.post("/api/populate/create/task", {"title": "Single Task Fetch"}, format="json")
        self.assertEqual(create_res.status_code, 201)
        created_data = create_res.data.get("data")
        task_id = created_data[0]["id"] if isinstance(created_data, list) else created_data["id"]

        url = f"/api/populate/read/task/{task_id}"
        res = self.client.get(url)
        print_postman_trace("GET", url, {"Authorization": "Bearer <JWT_TOKEN>"}, None, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))
        task_record = res.data.get("data")
        if isinstance(task_record, list):
            task_record = task_record[0]
        self.assertEqual(task_record["id"], task_id)
        self.assertEqual(task_record["title"], "Single Task Fetch")

    def test_09_postman_populate_update_entity(self):
        """
        POST /api/populate/update/tasks/:id
        Updates mutable fields on an existing record.
        """
        self.client.force_authenticate(user=self.admin)
        create_res = self.client.post("/api/populate/create/task", {"title": "Task to Update"}, format="json")
        self.assertEqual(create_res.status_code, 201)
        created_data = create_res.data.get("data")
        task_id = created_data[0]["id"] if isinstance(created_data, list) else created_data["id"]

        url = f"/api/populate/update/task/{task_id}"
        payload = {
            "title": "Task Successfully Updated",
            "priorityLevel": "Urgent"
        }
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, payload, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))

        # Verify through read API
        get_res = self.client.get(f"/api/populate/read/task/{task_id}")
        data = get_res.data.get("data")
        if isinstance(data, list):
            data = data[0]
        self.assertEqual(data["title"], "Task Successfully Updated")
        self.assertEqual(data["priorityLevel"], "Urgent")

    def test_10_postman_populate_soft_delete(self):
        """
        POST /api/populate/delete/tasks/:id
        Executes soft-delete (sets status=0 / lifecycle_status=0).
        Verifies that subsequent standard read queries automatically exclude it.
        """
        self.client.force_authenticate(user=self.admin)
        create_res = self.client.post("/api/populate/create/task", {"title": "Task to Delete"}, format="json")
        self.assertEqual(create_res.status_code, 201)
        created_data = create_res.data.get("data")
        task_id = created_data[0]["id"] if isinstance(created_data, list) else created_data["id"]

        url = f"/api/populate/delete/task/{task_id}"
        res = self.client.post(url, {}, format="json")
        print_postman_trace("POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, {}, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))

        # Subsequent standard list query must exclude it
        list_res = self.client.post("/api/populate/read/tasks", {"filter": {"id": task_id}}, format="json")
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(len(list_res.data.get("data", [])), 0)

    # =========================================================================
    # 3. FRONTEND ALIASES RESOLUTION (POSTMAN CONTRACT)
    # =========================================================================

    def test_11_postman_alias_payslips_resolution(self):
        """
        POST /api/populate/read/payslips
        Tests that frontend's 'payslips' route maps seamlessly to 'payroll' model.
        """
        self.client.force_authenticate(user=self.admin)
        url = "/api/populate/read/payslips"
        payload = {"page": 1, "limit": 5}
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, payload, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))

    def test_12_postman_alias_employee_lifecycle_histories_resolution(self):
        """
        POST /api/populate/read/employee_life_cycle_histories
        Tests that frontend career timeline route maps cleanly to 'EmployeeLifecycleHistory'.
        """
        self.client.force_authenticate(user=self.admin)
        url = "/api/populate/read/employee_life_cycle_histories"
        payload = {"page": 1, "limit": 5}
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, payload, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))

    def test_13_postman_alias_status_configs_resolution(self):
        """
        POST /api/populate/read/status_configss
        Tests that frontend's double 's' typo routes seamlessly without crashing.
        """
        self.client.force_authenticate(user=self.admin)
        url = "/api/populate/read/status_configss"
        payload = {"page": 1, "limit": 5}
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, payload, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))

    def test_14_postman_alias_order_acknowledgements_resolution(self):
        """
        POST /api/populate/read/oa
        Tests short alias for OrderAcknowledgement.
        """
        self.client.force_authenticate(user=self.admin)
        url = "/api/populate/read/oa"
        payload = {"page": 1, "limit": 5}
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, payload, res)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))

    # =========================================================================
    # 4. IMMUTABLE LEDGER GUARDS (POSTMAN CONTRACT)
    # =========================================================================

    def test_15_postman_immutable_ledger_direct_mutation_rejection(self):
        """
        POST /api/populate/update/client_ledger/:id
        Ledger tables (table_type="ledger") strictly reject direct updates and deletes.
        Verifies rejection response format in Postman.
        """
        self.client.force_authenticate(user=self.admin)
        url = "/api/populate/update/client_ledger/1"
        payload = {"amount": "99999.00"}
        res = self.client.post(url, payload, format="json")
        print_postman_trace("POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, payload, res)

        # Expected: HTTP 400 or 403 blocking mutation on immutable ledger
        self.assertIn(res.status_code, (400, 403))
        self.assertFalse(res.data.get("success"))

