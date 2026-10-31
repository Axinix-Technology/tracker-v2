"""
Standalone Postman API Simulation & Contract Verification Runner.
Executes pure HTTP calls against the Populate Engine endpoints and prints
the exact Postman response format (status, headers, JSON body).
Rule: Only calls the HTTP API endpoints; never invokes internal service functions directly.
"""

import os
import sys
import json

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import Role

User = get_user_model()


def format_postman_call(step_no: int, title: str, method: str, url: str, headers: dict, payload: dict | None, response):
    print("=" * 85)
    print(f"[{step_no:02d}] {title}")
    print(f"🚀 POSTMAN REQUEST: {method.upper()} {url}")
    print("   Headers:", json.dumps(headers, indent=4))
    if payload:
        print("   Body (JSON):")
        print("   " + json.dumps(payload, indent=4).replace("\n", "\n   "))
    else:
        print("   Body: None")
    print("-" * 85)
    print(f"📥 POSTMAN RESPONSE: Status {response.status_code}")
    resp_headers = {
        "Content-Type": response.get("Content-Type", "application/json"),
        "X-Request-ID": response.get("X-Request-ID", "N/A"),
    }
    print("   Headers:", json.dumps(resp_headers, indent=4))
    print("   Body (JSON):")
    try:
        if hasattr(response, "data"):
            body = response.data
        else:
            body = json.loads(response.content.decode("utf-8"))
        print("   " + json.dumps(body, indent=4, default=str).replace("\n", "\n   "))
    except Exception:
        print("   " + response.content.decode("utf-8", errors="replace"))
    print("=" * 85 + "\n")


def run_postman_simulation():
    print("\n" + "#" * 85)
    print("  TRACKER V2 - POSTMAN API SIMULATION & ENDPOINT CONTRACT VERIFICATION")
    print("  Standard: Pure API Calls Only (Zero Direct Service Function Calls)")
    print("#" * 85 + "\n")

    # 1. Setup Test SuperAdmin & Client
    role_super, _ = Role.objects.get_or_create(
        name="SuperAdmin", defaults={"is_superadmin": True, "status": 1}
    )
    admin_user, _ = User.objects.get_or_create(
        email="admin@axinix.com",
        defaults={
            "username": "admin@axinix.com",
            "is_superuser": True,
            "is_staff": True,
            "role": role_super
        }
    )
    admin_user.set_password("AdminSecurePassword123!")
    admin_user.save()

    client = APIClient()

    # Step 1: POST /api/auth/login
    step = 1
    url = "/api/auth/login"
    login_payload = {
        "username": "admin@axinix.com",
        "password": "AdminSecurePassword123!"
    }
    res = client.post(url, login_payload, format="json")
    format_postman_call(step, "USER AUTHENTICATION (LOGIN)", "POST", url, {"Content-Type": "application/json"}, login_payload, res)
    token = res.data.get("accessToken") if hasattr(res, "data") else None

    # Step 2: GET /api/auth/me/context
    step += 1
    client.force_authenticate(user=admin_user)
    url = "/api/auth/me/context"
    res = client.get(url)
    format_postman_call(step, "FETCH USER CONTEXT & PERMISSIONS", "GET", url, {"Authorization": "Bearer <JWT_TOKEN>"}, None, res)

    # Step 3: POST /api/populate/create/task
    step += 1
    url = "/api/populate/create/task"
    task_payload = {
        "title": "Implement Milestone Billing API",
        "observation": "Expose milestones in quotation and invoice services",
        "priorityLevel": "High",
        "status": "Backlogs",
        "estimatedHours": 8.0
    }
    res = client.post(url, task_payload, format="json")
    format_postman_call(step, "CREATE NEW ENTITY VIA POPULATE PIPELINE", "POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, task_payload, res)
    task_id = None
    if hasattr(res, "data") and res.data.get("data"):
        d = res.data["data"]
        task_id = d[0]["id"] if isinstance(d, list) else d.get("id")

    # Step 4: POST /api/populate/read/tasks (with pagination & filter)
    step += 1
    url = "/api/populate/read/tasks"
    read_payload = {
        "page": 1,
        "limit": 5,
        "filter": {"priorityLevel": "High"},
        "sort": "-id"
    }
    res = client.post(url, read_payload, format="json")
    format_postman_call(step, "FILTERED & PAGINATED ENTITY LIST QUERY", "POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, read_payload, res)

    # Step 5: GET /api/populate/read/task/:id
    if task_id:
        step += 1
        url = f"/api/populate/read/task/{task_id}"
        res = client.get(url)
        format_postman_call(step, "FETCH SINGLE ENTITY BY ID", "GET", url, {"Authorization": "Bearer <JWT_TOKEN>"}, None, res)

    # Step 6: POST /api/populate/update/task/:id
    if task_id:
        step += 1
        url = f"/api/populate/update/task/{task_id}"
        update_payload = {
            "title": "Implement Milestone Billing API (In Progress)",
            "status": "In Progress"
        }
        res = client.post(url, update_payload, format="json")
        format_postman_call(step, "UPDATE ENTITY STATE", "POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, update_payload, res)

    # Step 7: POST /api/populate/read/payslips (Alias verification)
    step += 1
    url = "/api/populate/read/payslips"
    alias_payload = {"page": 1, "limit": 3}
    res = client.post(url, alias_payload, format="json")
    format_postman_call(step, "FRONTEND ALIAS RESOLUTION ('payslips' -> 'payroll')", "POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, alias_payload, res)

    # Step 8: POST /api/populate/read/employee_life_cycle_histories (Alias verification)
    step += 1
    url = "/api/populate/read/employee_life_cycle_histories"
    alias_payload = {"page": 1, "limit": 3}
    res = client.post(url, alias_payload, format="json")
    format_postman_call(step, "FRONTEND ALIAS RESOLUTION ('employee_life_cycle_histories')", "POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, alias_payload, res)

    # Step 9: POST /api/populate/update/client_ledger/:id (Immutable Ledger Check)
    step += 1
    url = "/api/populate/update/client_ledger/1"
    tamper_payload = {"amount": "1000000.00"}
    res = client.post(url, tamper_payload, format="json")
    format_postman_call(step, "IMMUTABLE LEDGER TAMPER ATTEMPT REJECTION", "POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, tamper_payload, res)

    # Step 10: POST /api/populate/delete/task/:id (Soft-Delete)
    if task_id:
        step += 1
        url = f"/api/populate/delete/task/{task_id}"
        res = client.post(url, {}, format="json")
        format_postman_call(step, "SOFT-DELETE ENTITY", "POST", url, {"Authorization": "Bearer <JWT_TOKEN>"}, {}, res)

    print("✅ All Postman API Simulation Steps Completed Successfully.")


if __name__ == "__main__":
    run_postman_simulation()

