# Living Knowledge Brain: Two-Plane Decoupled Architecture & Modular Entitlements

> **Domain:** Control Plane Multi-Tenancy, Two-Plane Decoupling (Platform vs Client), `is_root_admin` vs `is_super_admin`, Granular Management Roles, and Subscription Lifecycle (Purchase, Upgrade, Degrade).  
> **Location:** `knowledge_brain/ControlPlane/MODULAR_ENTITLEMENTS_AUDIT.md`  
> **Related Files:**  
> - `backend/control_plane/models.py` (`PlatformRole`, `PlatformUser`, `Tenant`, `Module`)  
> - `backend/control_plane/registry.py` (Canonical plane & module mapping)  
> - `backend/control_plane/auth_views.py` (`PlatformLoginView`, `PlatformContextView`)  
> - `backend/users/authentication.py` (`DualTokenAndBearerAuthentication`)  
> - `backend/populate_core/policy/engine.py` (`PolicyEngine.authorize`)  
> - `backend/simulate_modular_entitlements_test.py`  
> - `backend/tests_api/test_modular_entitlements_audit.py`

---

## 1. Domain Problem & Resolution

### The Previous Conflation Flaw
Previously, SaaS Platform operations and Client ERP operations were mashed together into a single `User` and `Role` model. An organization's tenant administrator (`alice@acme.com`) was marked `is_superadmin = True`.
In the Populate Engine, `context.is_superadmin` granted a universal, unconditional bypass across:
1. **Platform Control Plane Resources** (`tenant`, `module`, `provisioning_run`).
2. **Unsubscribed Business Modules** (Payroll, CRM, Billing, Assets, Recruitment when only Attendance was purchased).
3. **Retention after Degrade** (Client retained access to cancelled modules).
4. **No Granular Staff Roles**: Impossible to create a platform management user who can view SaaS metrics and inspect tenants without mutation rights.

### The Two-Plane Decoupled Architecture (Implemented)
We established a strict physical and logical decoupling:

```
┌───────────────────────────────────────────────┬───────────────────────────────────────────────┐
│                PLATFORM PLANE                 │                 CLIENT PLANE                  │
│       (SaaS Control Plane Operations)         │            (Multi-Tenant ERP Ops)             │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ • Model: PlatformUser                         │ • Model: User                                 │
│ • Model: PlatformRole                         │ • Model: Role                                 │
│ • Authority: is_root_admin = True             │ • Authority: is_super_admin = True            │
│ • Roles: root_admin, management_viewer        │ • Roles: SuperAdmin, HRManager, Employee...   │
│ • Scope: Full bypass ONLY on Platform Models  │ • Scope: Bounded by tenant.enabled_modules    │
│ • Management Viewer: Read=Allow, Mutate=Block │ • Zero access to Platform Control Plane       │
└───────────────────────────────────────────────┴───────────────────────────────────────────────┘
```

---

## 2. Subscription Lifecycle Audit Matrix (Post-Implementation)

| Phase | Actor | Action / Resource | Subscribed? | HTTP Status | Verdict |
|---|---|---|---|---|---|
| **Phase 1** | `root_admin` | Read Tenants & Modules | Platform | `HTTP 200` | 🟢 Root Authorized |
| **Phase 2** | `management_viewer` | Read Tenants | Platform | `HTTP 200` | 🟢 Read Allowed |
| **Phase 2** | `management_viewer` | Mutate / Create Tenant | Platform | `HTTP 403` | 🟢 Blocked (`READ_ONLY_ROLE`) |
| **Phase 3** | `alice@acme.com` | Access Platform `module` | Platform | `HTTP 403` | 🟢 Blocked (`PLATFORM_ACCESS_FORBIDDEN`) |
| **Phase 4** | `alice@acme.com` | Attendance (`leave_type`) | Subscribed | `HTTP 200` | 🟢 Allowed |
| **Phase 4** | `alice@acme.com` | Core (`user`, `role`) | Core | `HTTP 200` | 🟢 Allowed |
| **Phase 4** | `alice@acme.com` | Payroll (`salary_structure`) | Unsubscribed | `HTTP 403` | 🟢 Blocked (`MODULE_NOT_SUBSCRIBED`) |
| **Phase 4** | `alice@acme.com` | CRM (`opportunity`) | Unsubscribed | `HTTP 403` | 🟢 Blocked (`MODULE_NOT_SUBSCRIBED`) |
| **Phase 4** | `alice@acme.com` | Billing (`quotation`) | Unsubscribed | `HTTP 403` | 🟢 Blocked (`MODULE_NOT_SUBSCRIBED`) |
| **Phase 5** | `alice@acme.com` | Payroll (After Upgrade) | Subscribed | `HTTP 200` | 🟢 Upgrade Activated |
| **Phase 5** | `alice@acme.com` | CRM (After Upgrade) | Unsubscribed | `HTTP 403` | 🟢 Still Blocked |
| **Phase 6** | `alice@acme.com` | Payroll (After Degrade) | Degraded | `HTTP 403` | 🟢 Revoked (`MODULE_NOT_SUBSCRIBED`) |

**Audit Result: 23 out of 23 probes passed with 0 permission leakages.**

---

## 3. Key Components Implemented

### 1. `backend/control_plane/models.py`
- `PlatformRole`: `role_id`, `name`, `is_root_admin`, `permissions`, `is_active`.
- `PlatformUser`: `email`, `username`, `password` (PBKDF2), `role = ForeignKey(PlatformRole)`.

### 2. `backend/control_plane/registry.py`
- Canonical categorization: `PLATFORM_MODELS`, `CLIENT_CORE_MODELS`, `CLIENT_BUSINESS_MODULES`.
- Helpers: `is_platform_model`, `is_core_model`, `get_module_for_model`, `is_model_entitled`.

### 3. `backend/users/authentication.py`
- Plane-aware `DualTokenAndBearerAuthentication`:
  - Decodes token `plane`.
  - Resolves `PlatformUser` for platform tokens (attaches `user.plane = "platform"`, `user.is_root_admin = True/False`).
  - Resolves `User` for client tokens (attaches `user.plane = "client"`, `user.is_super_admin = True/False`, `user.tenant_id`).

### 4. `backend/populate_core/policy/engine.py`
- **Platform Plane Check**:
  - `is_root_admin`: Full bypass on platform models.
  - `management_viewer`: Read/query allowed; mutations blocked with HTTP 403 `READ_ONLY_ROLE`.
  - Client users: Blocked with HTTP 403 `PLATFORM_ACCESS_FORBIDDEN`.
- **Client Plane Check**:
  - Core models: Allowed for active tenants.
  - Business modules: Checked against `tenant.enabled_modules`. Unsubscribed modules reject with HTTP 403 `MODULE_NOT_SUBSCRIBED`.
  - Client SuperAdmin bypass: Granted **only within active purchased modules and core**.

### 5. `backend/control_plane/auth_views.py` & `urls.py`
- Dedicated endpoint: `POST /api/platform/auth/login`.

---

## 4. Test Runners

1. **Interactive Visual Diagnostic Runner**:
   ```powershell
   backend\.venv\Scripts\python.exe backend\simulate_modular_entitlements_test.py
   ```
2. **Automated Django Test Case**:
   ```powershell
   backend\.venv\Scripts\python.exe backend\manage.py test tests_api.test_modular_entitlements_audit
   ```
