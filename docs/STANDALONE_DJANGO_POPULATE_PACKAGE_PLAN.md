# Architecture Specification & Plan: Standalone Reusable Django Populate Engine (`django-populate-core`)
## Pure, Decoupled Core Package for Instant Project Bootstrapping

> **Package Name**: `django-populate-core` (or `django-populate-engine`)  
> **Repository Type**: Standalone Git Repository (e.g. `git+https://github.com/<org>/django-populate-core.git`)  
> **Target Python**: Python 3.12+  
> **Target Framework**: Django 6.x + Django REST Framework 3.18+  
> **Philosophy**: Pure generic infrastructure only. **ZERO** business policies, **ZERO** domain models, **ZERO** hardcoded model strings.

---

## 1. Vision & Core Value Proposition

In Node.js ecosystems, developers easily install modular packages via `npm install` and initialize a functional backend server in minutes. The goal of `django-populate-core` is to deliver the exact same developer velocity for Python/Django:

1. **One-Line Install**: Any current or future project (E-commerce, Workhub Tracker, CRM, HRMS, Logistics) installs the engine via Git:
   ```bash
   pip install git+https://github.com/<org>/django-populate-core.git@v1.0.0
   ```
2. **Instant Initialization**: Add `'populate_core'` to `INSTALLED_APPS`, add middleware, mount `path('api/populate/', include('populate_core.urls'))`, and the entire 10-stage execution engine, AST query compiler, dynamic ABAC, and audit logger are instantly operational.
3. **Decoupled Single Source of Truth**: When bug fixes, query optimizations, or new caching algorithms are added to the core engine, a single version bump in Git (`v1.0.1`, `v1.1.0`) allows all downstream projects to upgrade seamlessly without breaking their domain business code.
4. **Zero Domain Leaks**: Core contains zero knowledge of products, carts, stock, attendance, or tasks. All business behavior is plugged in declaratively via:
   - `@register_model` on Django models
   - `BaseService` lifecycle hooks in downstream apps
   - Database-backed `AccessPolicy` records

---

## 2. Decoupling Audit: Eradicating Domain Leaks in `E-commerce/core`

Before moving `core` into its own repository, our automated audit identified specific domain leaks in `E-commerce\backend\core` that must be cleanly abstracted:

| File in `E-commerce/backend/core` | Identified Domain Leak | Decoupled Clean Architecture in `django-populate-core` |
|---|---|---|
| `core/models.py` | `AccessPolicy.role = ForeignKey("users.Role")` | Dynamic configurable Role setting: `getattr(settings, "POPULATE_ROLE_MODEL", settings.AUTH_USER_MODEL)` |
| `core/models.py` | `AuditLog.user = ForeignKey("users.User")` | Standard Django setting: `models.ForeignKey(settings.AUTH_USER_MODEL, ...)` |
| `core/crud/create.py` | Hardcoded `RESTRICTED_CREATE_MODELS = {"inventory_stock", "user_session"}` | Model-driven declarative flag: `@register_model("stock", allow_direct_create=False)` |
| `core/crud/delete.py` & `update.py` | Hardcoded `RESTRICTED_DELETE_MODELS = {"stock_ledger", "inventory_stock"}` | Model-driven table type: `@register_model("ledger", table_type="ledger", allow_delete=False, allow_update=False)` |
| `core/security/authentication.py` | `from catalogue.models import CustomerSession` | Pluggable session provider via `POPULATE_SESSION_HANDLER` setting |
| `core/utils/phone.py` | `from catalogue.models import CountryMaster` | Standard `phonenumbers` library with pure fallback (zero DB coupling) |
| `core/management/commands/` | `seed_areas.py`, `seed_geography.py`, `seed_states.py` | Purge ecommerce commands from core; keep only `init_populate` and `seed_core_defaults` |

---

## 3. Package Structure (`django-populate-core`)

```text
django-populate-core/
├── .gitignore
├── pyproject.toml                     # Modern PEP 621 / Poetry packaging
├── setup.cfg
├── README.md                          # Quickstart guide & API reference
├── LICENSE
├── populate_core/                     # Main Python package
│   ├── __init__.py                    # Exposes @register_model, BaseService, @register_service
│   ├── apps.py                        # Django AppConfig with registry bootstrapping
│   ├── urls.py                        # /<action>/<model_name>/[<object_id>]
│   ├── views.py                       # PopulateAPIView entrypoint
│   ├── middleware.py                  # ApiAuditLogMiddleware (X-Request-ID & audit recorder)
│   ├── models.py                      # AccessPolicy, AuditLog, GeneralSettings (Core-only)
│   ├── router.py                      # TenantDatabaseRouter (fail-closed multi-tenant routing)
│   ├── checks.py                      # Django system checks (utf8mb4, Redis in prod, DEBUG check)
│   ├── conf.py                        # Strict precedence configuration engine (Pydantic validated)
│   │
│   ├── registry/                      # Declarative Registry System
│   │   ├── __init__.py
│   │   ├── model_registry.py          # @register_model, table types, aliases, public_fields allowlist
│   │   ├── service_registry.py        # BaseService, @register_service, lifecycle hooks
│   │   ├── policy_registry.py         # In-memory policy cache & evaluator registry
│   │   └── relation_registry.py       # Relationship & join topology mapping
│   │
│   ├── pipeline/                      # Canonical 10-Stage Pipeline Engine (Fail-Fast Architecture)
│   │   ├── __init__.py
│   │   ├── context.py                 # RequestContext (tenant, identity, settings, correlation_id)
│   │   ├── observer.py                # PipelineObserver stage-by-stage latency telemetry
│   │   ├── stages.py                  # Canonical 10-stage implementations (preflight to audit)
│   │   └── executor.py                # PopulatePipeline.execute (fail-fast orchestrator)
│   │
│   ├── query/                         # AST & Parameterized Query Compilation
│   │   ├── __init__.py
│   │   ├── ast.py                     # AST node representations
│   │   ├── filters.py                 # Developer DSL -> AST parser (max depth 5, max nodes 25)
│   │   ├── builder.py                 # AST to QuerySet builder
│   │   ├── compiler.py                # SQL compiler (with session timeout & safe aggregate plans)
│   │   └── relation_resolver.py       # Automated select_related & prefetch_related (depth <= 3)
│   │
│   ├── policy/                        # ABAC, FBAC & Field-Level Authorization
│   │   ├── __init__.py
│   │   ├── engine.py                  # PolicyEngine with Redis cache & atomic invalidation
│   │   ├── context.py                 # PolicyContext
│   │   ├── evaluator.py               # Field allowlist projection (filters, order, groupBy, metrics)
│   │   └── conditions/                # FBAC Condition Registry
│   │       ├── __init__.py
│   │       ├── base.py                # is_owner (isSelf), matches_attribute
│   │       └── hierarchy.py           # is_manager, department_match
│   │
│   ├── security/                      # Defensive Guards & Ingress Firewalls
│   │   ├── __init__.py
│   │   ├── pre_validation_guard.py    # O(1) ingress checks (128-char password ceiling, 10MB body cap)
│   │   ├── identifier_guard.py        # Whitelist field name characters (anti-injection)
│   │   ├── lookup_guard.py            # Whitelist Django ORM lookup operators
│   │   ├── upload_guard.py            # Post-auth file validator (magic bytes, 25MP decompression bomb)
│   │   ├── sanitizer.py               # Mass-assignment defense & credential scrubber (anti-leak)
│   │   └── authentication.py          # Strict token tenant binding & Bearer/Session auth
│   │
│   ├── validation/                    # Schema & Payload Shape Checking
│   │   ├── __init__.py
│   │   ├── validator.py               # Pydantic schema validation
│   │   ├── rules.py                   # Business type validation rules
│   │   └── schemas/base.py
│   │
│   ├── crud/                          # Generic Action Handlers
│   │   ├── __init__.py
│   │   ├── create.py                  # Atomic insert with minimal DB lock window
│   │   ├── read.py                    # Filtered reads & keyset/offset pagination
│   │   ├── update.py                  # Atomic updates with state transition hooks
│   │   ├── delete.py                  # Atomic soft-delete handler (status=0)
│   │   ├── bulk.py                    # Chunked batch mutation handler (POPULATE_BULK_CHUNK_SIZE)
│   │   ├── aggregate.py               # Safe SQL GROUP BY and metric aggregator
│   │   └── export.py                  # Excel/CSV streaming with anti-formula injection prefix
│   │
│   ├── serialization/                 # Output Projection & Normalization
│   │   ├── __init__.py
│   │   ├── base.py                    # Streaming QuerySet iterator (chunk_size=1000)
│   │   └── output.py                  # public_fields allowlist projection & ensure_ascii=False
│   │
│   ├── response/                      # Standard JSON Response Envelopes & Crash Absorbers
│   │   ├── __init__.py
│   │   ├── exceptions.py              # PopulateEngineError hierarchy & UniversalCrashAbsorber
│   │   └── normalizer.py              # { "success": true, "data": ..., "count": ... }
│   │
│   ├── audit/                         # Non-Blocking Audit Trail Subsystem
│   │   ├── __init__.py
│   │   ├── logger.py                  # AuditLogger engine with async thread worker pool
│   │   └── helpers.py                 # record_audit_log, credential scrubber (passwords/tokens)
│   │
│   ├── modules/                       # Optional Pluggable Extension Subsystems (Feature-Flagged)
│   │   ├── __init__.py
│   │   ├── workflows/                 # Declarative Approval & State Transition Engine
│   │   │   ├── __init__.py
│   │   │   ├── models.py              # GenericWorkflow, WorkflowStep, WorkflowTransition
│   │   │   ├── engine.py              # Dynamic state machine & transition validator
│   │   │   └── service.py             # Lifecycle hooks integration
│   │   │
│   │   ├── notifications/             # Dual-Model In-App & Push Notification Engine
│   │   │   ├── __init__.py
│   │   │   ├── models.py              # NotificationContent, NotificationRecipient
│   │   │   ├── dispatcher.py          # Multicast dispatcher (In-App, FCM, Email, Webhook)
│   │   │   └── fcm.py                 # FCM Push backend
│   │   │
│   │   └── queue/                     # Async Background Job Queue
│   │       ├── __init__.py
│   │       ├── job_queue.py           # Non-blocking async queue with retry delay & concurrency
│   │       └── worker.py              # Lightweight task worker with SIGTERM drain
│   │
│   └── management/
│       └── commands/
│           ├── init_populate.py       # Scaffolding helper for new projects
│           ├── check_populate_indexes.py # Scans for missing soft-delete composite indexes
│           ├── archive_audit_logs.py  # Monthly partition archival to S3
│           └── seed_core_policies.py  # Generates baseline AccessPolicy rows
│
└── tests/                             # Standalone Test Suite
    ├── runtests.py                    # Standalone test runner
    ├── test_settings.py               # Lightweight in-memory SQLite / MySQL test config
    ├── test_pipeline.py
    ├── test_query_compiler.py
    └── test_abac_policies.py
```

---

## 3.1 Architectural Principle: Core Kernel vs. Pluggable Extension Modules

A core design requirement is **absolute modularity without bloat**:
> *"A package might contain something that is useful for one project, but NOT useful for another project. That distinction matters."*

To satisfy this rule permanently, `django-populate-core` is structured in two distinct tiers:

### Tier 1: The Core Kernel (Mandatory, Universal, Ultra-Fast)
Every project without exception needs:
- The 10-Stage Populate Pipeline & REST endpoint (`/api/populate/`)
- AST Query Compiler, joins, filters, ordering, and pagination
- Model & Service Registries (`@register_model`, `BaseService`)
- Dynamic DB-backed `AccessPolicy` & Superadmin bypass
- Identifier guards, lookup whitelists, and payload sanitization
- Immutable MySQL `AuditLog` & `X-Request-ID` tracing

*E-commerce uses this Tier alone. It runs with zero extra tables, zero unused background workers, and zero performance overhead.*

### Tier 2: Pluggable Extension Modules (Opt-In Feature Flags)
Certain enterprise projects (such as Workhub Tracker, HRMS, CRM) require workflow approvals or notification queues. These live as optional modules under `populate_core.modules`:

1. **Workflow & Approval Engine (`modules/workflows`)**:
   - **Zero Hardcoded Enums**: Does NOT hardcode model names like `leaves` or `tickets`. Any registered model can participate in approval workflows declaratively via `@register_model(has_workflow=True)`.
   - **Generic State Machine**: Dynamic steps, timeout hours, actor resolution (reporting manager, role, specific user), and status transition gates.
   - **Dormant by Default**: If `ENABLE_WORKFLOWS = False`, zero tables are registered, zero migrations are run.

2. **Dual-Model Notification Engine (`modules/notifications`)**:
   - **Dual Model**: `NotificationContent` (single event payload) + `NotificationRecipient` (delivery states: read, clicked, fcmStatus).
   - **Pluggable Dispatchers**: In-App, FCM Push, Email, Webhooks.
   - **Dormant by Default**: If `ENABLE_NOTIFICATIONS = False`, zero notification tables or workers exist.

3. **Async Job Queue (`modules/queue`)**:
   - Non-blocking local background worker for deferred dispatching (push notifications, webhook calls) without locking HTTP requests.
   - Zero external infrastructure required (falls back to local async thread worker if Redis is absent).

### Strict Prohibition of Domain Knowledge Leaks ("End of the Road")
Neither Tier 1 nor Tier 2 will EVER contain business-specific domain strings:
- **NO** ecommerce terms (`cart`, `stock`, `inventory`, `orders`, `products`).
- **NO** tracker/HR terms (`leaves`, `tickets`, `attendance`, `payroll`, `onboarding`).
- All models, fields, and workflows are registered dynamically at runtime by the downstream application.

---

## 3.2 The Canonical 10-Stage Pipeline Sequence (Fail-Fast & CPU-Protective Architecture)

The pipeline is the primary line of defense against CPU waste, runaway memory, and unauthorized access. 

> **The Golden Pipeline Law**: *Never perform expensive work (streaming uploads to S3, AST planning, validation, database connections) before the caller is authenticated, rate-checked, and authorized. The pipeline must fail fast at the earliest possible stage to protect CPU and memory.*

### Canonical Stage Sequence Table

| Stage # | Stage Name | Primary Responsibilities | Why It Sits Here (CPU & Security Rationale) | Fail Status |
|---|---|---|---|---|
| **Stage 01** | **Pre-Flight Limits & Ingress Firewall** (`PreFlightStage`) | • Header Content-Length inspection (`<= 10MB`).<br>• $O(1)$ Password length check (`<= 128 chars`).<br>• `X-Request-ID` generation/propagation.<br>• Client IP extraction (`X-Forwarded-For`). | Kills brute-force DoS and gigantic payloads in **`<0.01ms`** before reading payload into memory or running CPU-heavy Bcrypt hashing. | `HTTP 400` / `HTTP 413` |
| **Stage 02** | **Ingress Parsing & Action Normalization** (`IngressParseStage`) | • Safe JSON parsing (recursion depth cap $\le 10$).<br>• Multipart boundary inspection (does **NOT** upload to S3 yet).<br>• Canonical action (`read`, `create`, `update`, `delete`, `bulk`, `aggregate`, `export`) and model resolution. | Prevents Python `RecursionError` call stack bombs. Normalizes actions without allocating heavy memory buffers. | `HTTP 422` |
| **Stage 03** | **Tenant Resolution & Identity Binding** (`AuthContextStage`) | • **Strict Tenant Binding**: Authenticated tokens bind tenant **strictly from the token `tid` claim**. The client `X-Tenant-Id` header is **forbidden** from picking/overriding tenant (anti-token replay). Anonymous requests resolve tenant from subdomain or header.<br>• Bearer JWT / Session authentication.<br>• Binds cached `GeneralSettings` singleton (timezone, currency). | Identifies WHO is asking and WHICH database they belong to. Essential before throttling and authorization. | `HTTP 400` / `HTTP 401` |
| **Stage 04** | **Dynamic Rate Limiting & Throttling** (`RateLimitStage`) | • Evaluates rate limits using shared Redis counters: Anonymous IP (60/min), User (600/min), Telemetry (600/min).<br>• Idempotency key pre-check: if `X-Idempotency-Key` exists and matches cached hash, returns cached response instantly. | Runs **after** identity is resolved so throttling is tracked accurately per user/tenant in Redis, halting abusive scrapers in **`<0.1ms`**. | `HTTP 429` |
| **Stage 05** | **Authorization & Entitlement Gate** (`AuthorizationStage`) | • Module license check (`RequestContext.tenant_context['enabled_modules']`).<br>• `PUBLIC_READ_MODELS` / `PUBLIC_CREATE_MODELS` allowlist check.<br>• ABAC/RBAC dynamic policy evaluation (`can_read`, `can_create`, etc.).<br>• `IMMUTABLE_MODELS` / `READ_ONLY_MODELS` mutation block.<br>• `GLOBAL_MODELS` tenant write block.<br>• Export permission gate (`can_export`). | **The Fail-Fast Firewall**: Rejects unauthorized callers with 401/403 **BEFORE** any file upload starts, before AST query compilation, and before database connection acquisition. Zero wasted compute. | `HTTP 401` / `HTTP 403` / `HTTP 405` |
| **Stage 06** | **Validation, Field Policy & Secure Uploads** (`ValidationStage`) | • Schema & Pydantic type validation.<br>• Field policy projection: removes forbidden fields from payload, filters, order, and `groupBy`/`metrics`.<br>• Anonymous reads clamped to model `public_fields` allowlist.<br>• **Secure File Upload**: Only now are multipart file bytes validated (magic bytes, 10MB cap, 25MP decompression bomb guard) and streamed to S3/R2 in tenant-namespaced paths (`tenant/<tid>/<mod>/...`). | Guarantees that files are streamed to S3 **ONLY** for authorized, valid requests, completely eliminating orphan upload storage attacks. | `HTTP 400` / `HTTP 422` |
| **Stage 07** | **AST Query Compilation & Join Planning** (`CompilationStage`) | • AST query parsing (depth cap $\le 5$, node count $\le 25$, `$in` size $\le 100$).<br>• Model limit overrides resolved (`Decorator > POPULATE_CONFIG > .env > Default`).<br>• Automated `select_related` and `prefetch_related` joins planned up to allowed depth ($\le 3$).<br>• Parameterized SQL compilation (zero string concatenation). | Plans the most efficient relational execution plan without triggering N+1 queries or memory-heavy join trees. | `HTTP 400` / `HTTP 422` |
| **Stage 08** | **Execution, Transaction & Hook Orchestration** (`ExecutionStage`) | • Query Cache Hit: If `cache_ttl > 0` and cached in Redis, returns in <2ms, skipping DB.<br>• Session limits set on connection: `max_execution_time = 5000; innodb_lock_wait_timeout = 5`.<br>• **Service `before_*` Hooks (Fail-Closed)**: Aborts transaction and rolls back if validation fails.<br>• Atomic execution inside `transaction.atomic()` (auto-rollback on `dry_run=true`).<br>• **Service `after_*` Hooks (Fail-Safe)**: Side effects (FCM, email, queue) registered strictly on `transaction.on_commit`. | Guarantees data integrity. `before_*` hooks protect the DB; `after_*` side effects run only after MySQL commit succeeds, preventing ghost side effects. | `HTTP 400` / `HTTP 500` / `HTTP 504` |
| **Stage 09** | **Serialization & Output Sanitization** (`SerializationStage`) | • OOM-Safe QuerySet streaming: `QuerySet.iterator(chunk_size=1000)`.<br>• Output field masking per policy.<br>• **CSV Formula Injection Defense**: Prefixes `=`, `+`, `-`, `@` with `'` on exports.<br>• Signed, short-lived download links bound to tenant & user.<br>• Native Tamil/Indic Unicode serialization (`ensure_ascii=False`). | Eliminates memory crashes on large responses and prevents spreadsheet formula execution vulnerabilities. | `HTTP 500` |
| **Stage 10** | **Finalization, Response & Non-Blocking Audit** (`FinalizationStage`) | • Caches response envelope in Redis if `X-Idempotency-Key` was supplied (TTL 300s).<br>• Returns JSON response to client immediately (**`<5ms`**).<br>• **Non-Blocking Audit**: Offloads sanitized audit row (`user`, `ip`, `path`, `action`, sanitized `changes`) to async worker thread pool. Skips read audit if `audit_reads=False`. Unbound tenant errors write to control DB. | Leaves the client connection closed instantly while background auditing executes asynchronously without holding HTTP threads. | Response Delivered |

---

## 4. How Downstream Projects Use It (The Developer Experience)

Just like initializing Express in Node, initializing a project with `django-populate-core` requires only 4 declarative steps:

### Step 1: Install via Git in `requirements.txt`
```text
# requirements.txt
django>=6.1.1
djangorestframework>=3.18.1
mysqlclient>=2.3.0
django-populate-core @ git+https://github.com/<your-org>/django-populate-core.git@v1.0.0
```

### Step 2: Configure `settings.py`

#### Scenario A: Lean E-commerce Configuration (Core Kernel Only — Zero Overhead)
```python
INSTALLED_APPS = [
    # Standard Django apps ...
    'rest_framework',
    'corsheaders',
    'populate_core',      # <--- Reusable Core Engine
    'catalogue',          # E-commerce apps
    'orders',
]

POPULATE_CONFIG = {
    'ROLE_MODEL': 'users.Role',
    'SUPERADMIN_ROLE_FLAG': 'is_superadmin',
    'MAX_PREFETCH_DEPTH': 3,
    'CHILD_PAGINATION_CEILING': 50,
    # Extensions disabled: E-commerce stays ultra-lean with 0 extra tables
    'ENABLE_WORKFLOWS': False,
    'ENABLE_NOTIFICATIONS': False,
}
```

#### Scenario B: Advanced Workhub Tracker Configuration (Kernel + Workflows + Notifications)
```python
INSTALLED_APPS = [
    # Standard Django apps ...
    'rest_framework',
    'corsheaders',
    'populate_core',      # <--- Reusable Core Engine
    'users',              # Tracker apps
    'tasks',
    'daily_status',
]

POPULATE_CONFIG = {
    'ROLE_MODEL': 'users.Role',
    'SUPERADMIN_ROLE_FLAG': 'is_superadmin',
    'MAX_PREFETCH_DEPTH': 3,
    'CHILD_PAGINATION_CEILING': 50,

    # 1. Models allowing unauthenticated Read (branding, public catalog, settings)
    'PUBLIC_READ_MODELS': ['general_settings', 'company'],

    # 2. Models allowing unauthenticated Create (leads, job applicants, contact inquiries)
    'PUBLIC_CREATE_MODELS': ['lead', 'candidate', 'contact_inquiry'],

    # 3. Global / Master models that bypass tenant-id scoping (countries, currencies, plans)
    'GLOBAL_MODELS': ['country', 'currency_master', 'system_plan'],

    # 4. Immutable Ledger models where update & delete are strictly blocked by engine (HTTP 405)
    'IMMUTABLE_MODELS': ['payment_journal', 'audit_log', 'asset_stock_ledger'],

    # 5. Read-Only System Lookups where create, update, delete are blocked via API
    'READ_ONLY_MODELS': ['capability', 'status_config', 'leave_types'],

    # 6. High-Frequency Telemetry models with relaxed rate limits (biometrics, screen heartbeat)
    'HIGH_FREQUENCY_MODELS': ['time_tracker_session', 'attendance_punch'],

    # 7. Highly sensitive models requiring superadmin permissions for bulk CSV/Excel export
    'RESTRICTED_EXPORT_MODELS': ['payroll', 'salary_structure', 'agent_tokens'],

    # Extensions enabled declaratively
    'ENABLE_WORKFLOWS': True,
    'ENABLE_NOTIFICATIONS': True,
    'FCM_SERVER_KEY': env('FCM_SERVER_KEY', default=''),
}
```

### Step 3: Mount URLs in `config/urls.py`
```python
from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('users.urls')),
    path('api/populate/', include('populate_core.urls')),  # <--- Instantly exposes generic CRUD
]
```

### Step 4: Define Domain Models & Services in Downstream Apps
```python
# tasks/models.py
from django.db import models
from populate_core.registry import register_model

@register_model("task", table_type="transactional")
class Task(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

# tasks/services.py
from populate_core.registry import BaseService, register_service

@register_service("task")
class TaskService(BaseService):
    def before_create(self, context, payload):
        # Custom domain validation, notifications, side effects
        return payload
```

*That is all!* The model is automatically accessible at `/api/populate/read/task`, `/api/populate/create/task`, with full AST filtering, join planning, ABAC access checks, and audit logging.

---

### 4.1 The Developer Freedom & Anti-Frustration Cookbook
*(How to Handle Any Complex Requirement in Populate Without Stressing Out or Building Custom Routes)*

When engineering teams enforce Sacred Rule 8 (*"Strict Prohibition on Redundant Routers & Controllers"*), developers frequently stress out and think: *"Populate is too rigid for my use case; I have to build a custom endpoint!"*

The Populate Engine is designed to handle **100% of standard and complex enterprise business logic**. Below is the developer cookbook for every common scenario:

#### 1. Custom Business Actions & State Transitions ("Approve", "Reject", "Cancel", "Publish")
- **The Dev Temptation**: `POST /api/leave/123/approve` or `POST /api/order/123/cancel`.
- **The Populate Way**: Use standard update with an `action_intent` parameter:
  ```http
  POST /api/populate/update/leave/123
  Content-Type: application/json

  {
    "action_intent": "approve",
    "approver_remarks": "Approved after workload review"
  }
  ```
- **In `LeaveService`**:
  ```python
  @register_service("leave")
  class LeaveService(BaseService):
      def before_update(self, context, instance, payload):
          if payload.get("action_intent") == "approve":
              self.validate_approval_permission(context, instance)
              payload["status"] = LeaveStatus.APPROVED
              payload["approved_at"] = timezone.now()
              payload["approved_by"] = context.user
          return payload

      def after_update(self, context, instance, changes):
          if changes.get("status") == LeaveStatus.APPROVED:
              self.trigger_approval_notification(instance)
              self.decrement_leave_balance(instance)
  ```
  *Benefit*: Inherits RBAC, correlation ID, non-blocking audit logging, and transactional safety automatically.

#### 2. Bulk / Batch Operations ("Close 50 Tickets", "Bulk Assign")
- **The Dev Temptation**: `POST /api/tickets/bulk-close`.
- **The Populate Way**: Built-in `/api/populate/bulk_update/<model>`:
  ```http
  POST /api/populate/bulk_update/ticket
  Content-Type: application/json

  {
    "ids": [101, 102, 103, 104],
    "data": { "status": "CLOSED", "resolution": "Resolved via bulk patch" }
  }
  ```
  *Benefit*: Executes inside a single database transaction, runs service lifecycle hooks for each item, clamps memory usage via `POPULATE_BULK_CHUNK_SIZE`, and records audit entries.

#### 3. Complex Aggregations & Dashboard Analytics (Group By, Sum, Monthly Metrics)
- **The Dev Temptation**: `GET /api/dashboard/stats` or `GET /api/reports/sales-by-month`.
- **The Populate Way**: Built-in `/api/populate/aggregate/<model>`:
  ```http
  POST /api/populate/aggregate/ticket
  Content-Type: application/json

  {
    "filter": { "created_at": { "$gte": "2026-01-01" } },
    "groupBy": ["department", "status"],
    "metrics": {
      "total_tickets": "$count",
      "avg_resolution_hours": { "$avg": "resolution_hours" },
      "critical_count": { "$count": { "priority": "CRITICAL" } }
    }
  }
  ```
  *Benefit*: Compiles directly to optimized SQL `GROUP BY` with strict field policy enforcement on `groupBy` and `metrics` (preventing users from inferring restricted fields like `salary` via grouping). Automatically runs within the caller's isolated tenant database.

#### 4. File & Image Uploads with Records (Multipart Form-Data)
- **The Dev Temptation**: `POST /api/employees/123/upload-avatar` or `POST /api/tasks/create-with-attachment`.
- **The Populate Way**: `/api/populate/create/<model>` and `/api/populate/update/<model>/<id>` natively accept `multipart/form-data`:
  ```http
  POST /api/populate/create/ticket
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="data"
  {"title": "Broken Server", "priority": "CRITICAL", "description": "See attached log"}
  ------WebKitFormBoundary
  Content-Disposition: form-data; name="attachment"; filename="server_log.txt"
  Content-Type: text/plain
  ...file bytes...
  ------WebKitFormBoundary--
  ```
  *Benefit*: **Post-Auth Upload Processing**: Stage 6 (`ValidationStage`) executes **only after** identity authentication and authorization pass. It validates file magic bytes, enforces the 25MP decompression bomb limit and 10MB file ceiling, streams the file to S3/R2 in a tenant-namespaced path (`tenant/<tid>/<mod>/...`), and injects the resulting URL into `payload['attachment_url']` before `before_create`. Unauthorized callers are rejected in Stage 5 before a single byte touches S3.

#### 5. Dry-Run / Preview Calculations (Tax Preview, Overtime Math, Leave Balances)
- **The Dev Temptation**: `POST /api/payroll/calculate` or `POST /api/leave/preview-balance`.
- **The Populate Way**: Send standard mutation request with query parameter `?dry_run=true`:
  ```http
  POST /api/populate/create/payroll_run?dry_run=true
  Content-Type: application/json

  { "employee_id": 42, "month": 10, "year": 2026 }
  ```
  *Benefit*: The engine runs full validation, computes all formulas in `before_create`, builds the response payload with all calculated numbers, and **rolls back the database transaction**. The client gets the exact calculated preview with zero phantom database rows.

#### 6. Multi-Model Atomic Sagas (Nested Creates: Order + 5 Items + 1 Shipment)
- **The Dev Temptation**: `POST /api/orders/checkout`.
- **The Populate Way**: Send nested JSON payload to `/api/populate/create/order`:
  ```json
  {
    "customer_id": 10,
    "items": [
      { "product_id": 101, "quantity": 2 },
      { "product_id": 204, "quantity": 1 }
    ],
    "shipping_address": "..."
  }
  ```
- **In `OrderService.before_create`**:
  ```python
  def before_create(self, context, payload):
      items_data = payload.pop("items", [])
      # Parent Order is created by pipeline; child items are created in after_create
      context.stash["items_data"] = items_data
      return payload

  def after_create(self, context, instance):
      items_data = context.stash.get("items_data", [])
      OrderItem.objects.bulk_create([
          OrderItem(order=instance, **item) for item in items_data
      ])
  ```

#### 7. Export to Excel / CSV
- **The Dev Temptation**: `GET /api/tickets/export-excel`.
- **The Populate Way**: Built-in `/api/populate/export/<model>?format=xlsx|csv`:
  Takes the exact same AST filter payload as the table read view. Streams file directly or dispatches to the background worker pool if rows exceed `POPULATE_BULK_CHUNK_SIZE`.

---

### 4.2 The 3-Point Strict Exemption Policy (When a Custom Route IS Legitimate)

To eliminate developer guilt and ensure absolute clarity, a dedicated custom router/controller is **ONLY permitted** if it meets at least one of these 3 physical criteria:

1. **Raw Cryptographic Signature Verification**: Webhooks requiring verification of raw, unparsed HTTP request body bytes before JSON parsing (e.g., Stripe `stripe-signature`, Razorpay HMAC-SHA256, GitHub webhooks).
2. **Stateful Session Handshakes**: Interactive multi-step authentication handshakes (e.g., OAuth2 redirects, SAML/SSO callbacks, WebAuthn/FIDO2 credentials).
3. **Continuous Binary Streaming**: Non-JSON streaming pipelines where buffering into memory or S3 is impossible (e.g., real-time audio/video transcoding pipes or streaming a 5GB dynamic ZIP backup).

*If an engineering requirement does not meet one of these 3 physical criteria, it MUST be handled via `populate` + `services/<model>.py`.*

---

### 4.3 The 7 Declarative Model Governance Policies
*(Why Normal Developers Build Custom Routes & How We Solve Them via Declarative `.env` / Config)*

Just as `PUBLIC_READ_MODELS` solved the unauthenticated company branding dilemma without custom controllers, there are **7 other classic scenarios** where a normal developer looks at standard engine behavior, feels blocked, and reflexively builds a custom route.

Instead of writing custom routers, `django-populate-core` provides declarative policies configured via `POPULATE_CONFIG` or `.env`:

| # | Why a Normal Developer Builds a Custom Route | What the Developer Fears | Declarative Engine Solution (`.env` / `POPULATE_CONFIG`) | Engine Behavior |
|---|---|---|---|---|
| **1** | **Public Form Submissions (`leads`, `candidates`, `inquiries`)** | *"Populate blocks `create` without a Bearer token (401). Careers & Contact pages are for anonymous visitors! I must make `POST /api/leads`."* | **`PUBLIC_CREATE_MODELS`**<br>`POPULATE_PUBLIC_CREATE_MODELS=lead,candidate,contact_inquiry` | Stage 4 permits anonymous `create`. Automatically runs through anti-spam honeypot guards and anonymous rate-limiting (`POPULATE_RATE_LIMIT_ANON`). |
| **2** | **Global Master Data (`countries`, `currencies`, `plans`)** | *"Populate injects tenant-id scoping or connects to tenant DB. But countries belong to no tenant! Queries fail or return 0 rows. I must make `GET /api/global/countries`."* | **`GLOBAL_MODELS`**<br>`POPULATE_GLOBAL_MODELS=country,currency_master,system_plan` | The AST Query Compiler and Database Router automatically bypass tenant scoping and route queries directly to the primary/control database. |
| **3** | **Immutable Financial & Stock Ledgers (`payment_journal`, `asset_stock_ledger`)** | *"Populate exposes generic `update` and `delete`! A user could send a PUT/DELETE and tamper with accounting balances. I must make a custom route that only accepts POST!"* | **`IMMUTABLE_MODELS`**<br>`POPULATE_IMMUTABLE_MODELS=payment_journal,audit_log,asset_stock_ledger` | The engine physically disables mutation: `update` and `delete` are blocked with **HTTP 405 Method Not Allowed**. Rows can only be appended. |
| **4** | **System Master Lookups (`capability`, `sidebar`, `status_config`)** | *"Populate allows admins with CRUD rights to accidentally create, edit, or delete core system constants via REST API. I must make a custom read-only route!"* | **`READ_ONLY_MODELS`**<br>`POPULATE_READ_ONLY_MODELS=capability,sidebar,status_config` | Disables `create`, `update`, and `delete` via the public API. Mutations are strictly restricted to internal migration scripts and management commands. |
| **5** | **High-Frequency Telemetry (`attendance_punch`, `screen_heartbeat`)** | *"Biometric IoT punch machines or time trackers ping every 5 seconds. Populate's global 60 req/min rate limit throttles our machines with 429! I must make an unthrottled custom route!"* | **`HIGH_FREQUENCY_MODELS`**<br>`POPULATE_HIGH_FREQUENCY_MODELS=time_tracker_session,attendance_punch` | Assigns these models to a dedicated high-capacity telemetry rate limit pool (e.g. 600 req/min per device) without compromising overall API security. |
| **6** | **Restricted Data Exports (`payroll`, `salary_structure`, `agent_token`)** | *"Any user with read access might call `/api/populate/export/payroll` and dump confidential company salaries to Excel! I must block export and write a custom route!"* | **`RESTRICTED_EXPORT_MODELS`**<br>`POPULATE_RESTRICTED_EXPORT_MODELS=payroll,salary_structure,agent_token` | The export pipeline strictly rejects export jobs unless the requester is explicitly verified as a SuperAdmin (`context.user.is_superadmin == True`). |
| **7** | **Soft-Delete vs Physical Purge** | *"Populate's `/delete` will physically drop rows from MySQL, breaking historical foreign keys! I must build a custom `POST /api/tickets/archive` route!"* | **`SOFT_DELETE_MODELS`**<br>`POPULATE_SOFT_DELETE_FIELD=status`<br>`POPULATE_SOFT_DELETE_MODELS=*` | Calling `/api/populate/delete/<model>/<id>` executes an atomic soft-delete (`status=0` or `deleted_at=now()`) rather than physical SQL `DELETE`. |

---

### 4.4 Granular Pipeline Directives & Per-Model Limit Overrides
*(Safe Defaults Globally, Flexible Tuning Locally)*

A rigid, one-size-fits-all pipeline creates severe operational bottlenecks:
- If a global query timeout is 5 seconds, an annual tax report or financial reconciliation model will time out and fail.
- If every single `read` on high-traffic models (`general_settings`, `notifications`, `time_tracker_session`) is written to `audit_logs`, the database will bloat with 10,000,000+ useless audit rows.
- If a low-frequency analytical model needs a deeper join tree (depth 4 or 5), the global ceiling of 3 rejects it.

To solve this cleanly, `django-populate-core` adopts the **"Safe Defaults Globally, Flexible Tuning Locally"** architecture:

#### 1. What CANNOT Be Bypassed (The Non-Negotiable Invariants)
These 4 security foundations are hard-coded into the pipeline kernel and can **never** be bypassed:
1. **Parameterized SQL Compilation**: All AST queries compile to parameterized queries (zero SQL injection).
2. **Tenant Boundary Scoping**: Tenant data-plane isolation is enforced fail-closed.
3. **ABAC / RBAC Authorization**: Role capabilities and field allow/forbidden policies are always evaluated.
4. **Dangerous Input Sanitization**: Script tags, SQL comments, and forbidden private fields are strictly scrubbed.

#### 2. What CAN Be Selectively Tuned or Bypassed Per Model (Operational Agility)

| Operational Stage | Global Default | Per-Model Override Option | Developer Use Case |
|---|---|---|---|
| **Stage 10: Read Auditing** | `audit_reads=False` (Only mutations audited) | `@register_model(audit_reads=True)` or `POPULATE_AUDIT_READ_MODELS=payroll` | High-frequency models (`settings`, `telemetry`) skip read audits to save DB disk/IO; sensitive models (`payroll`, `bank_accounts`) opt-in to full read auditing. |
| **Stage 06: Join Depth** | `MAX_PREFETCH_DEPTH=3` | `@register_model(max_prefetch_depth=5)` | Allows complex analytical models (e.g. `annual_report`) to join across 5 tables while standard transactional models stay clamped at 3. |
| **Stage 07: Query Timeout** | `QUERY_TIMEOUT_MS=5000` (5s) | `@register_model(query_timeout_ms=15000)` | Grants heavy reconciliation jobs a 15-second window while protecting fast OLTP APIs at 5s. |
| **Stage 08: In-Memory / Redis Caching** | `cache_ttl=0` (Always hit DB) | `@register_model(cache_ttl=300)` | Master lookup tables (`departments`, `currencies`, `countries`) are served directly from Redis in <2ms, bypassing the database completely. |
| **Stage 05: Max Page Size** | `MAX_PAGE_LIMIT=100` | `@register_model(max_page_limit=500)` | Reporting models can return up to 500 rows for charting while standard grids are clamped to 100 rows. |
| **Stage 08: Safe Aggregations** | `allow_aggregations=False` on raw transactional tables | `@register_model(allow_aggregations=True)` | Prevents expensive `GROUP BY` and `COUNT` queries on un-indexed 10M row tables, but unlocks them on models with verified indexes. |

#### Example: Declaring Model Overrides
```python
# reports/models.py
from populate_core.registry import register_model

@register_model(
    "annual_reconciliation",
    max_prefetch_depth=5,        # Higher join depth for multi-ledger reports
    query_timeout_ms=15000,      # 15s timeout for heavy reporting
    max_page_limit=500,          # Allow 500 rows for financial exports
    audit_reads=True,            # Opt-in to read auditing for sensitive financial statements
    allow_aggregations=True      # Permit safe GROUP BY queries
)
class AnnualReconciliation(models.Model):
    ...
```

Or configured centrally in `POPULATE_CONFIG`:
```python
POPULATE_CONFIG = {
    'MODEL_RESOURCE_OVERRIDES': {
        'annual_reconciliation': {
            'MAX_PREFETCH_DEPTH': 5,
            'QUERY_TIMEOUT_MS': 15000,
            'MAX_PAGE_LIMIT': 500,
            'AUDIT_READS': True,
        },
        'general_settings': {
            'CACHE_TTL': 3600,       # Cache for 1 hour
            'AUDIT_READS': False,    # Skip read audit bloat
        }
    }
}
```

---

## 5. Master Production Edge-Case & Hardening Matrix (The 27 Core Defenses)

Because `django-populate-core` is the central engine powering multiple production applications (Workhub Tracker, E-commerce, CRM, and future platforms) for 6+ months without maintenance churn, it is hardened against all 27 known production edge cases, security vulnerabilities, and database failure modes:

### Master Production Edge-Case & Defense Matrix

| # | Subsystem / Description | Production Edge / Threat | Non-Negotiable Engineering Defense |
|---|---|---|---|
| **01** | **Tenant registry & resolution** | A client-supplied `X-Tenant` header plus a valid token from tenant A can reach tenant B (cross-tenant token replay). | Include `tid` (tenant ID) claim in the token; enforce strict equality with the resolved tenant. Reject on mismatch. Unknown tenant returns a single generic error. |
| **02** | **Fail-closed tenant router** | Management commands, shell, background workers, or missed code paths silently read or write the wrong database. | Database router raises an exception when no tenant is bound (fail closed). Shared/system models route explicitly to the control DB. |
| **03** | **Tenant context in async work** | The tenant binding is lost when audit logging and job queues execute on thread pools, writing rows to the wrong tenant or default DB. | Use Python `contextvars` and pass explicit `tenant_id` in every job and audit payload. Worker re-binds context before any DB call. |
| **04** | **Connection explosion** | With 100+ tenants, separate connection sets per tenant database exhaust MySQL `max_connections`, leaking connections across workers. | Implement a bounded LRU connection registry. Automatically close idle tenant connections. Size `CONN_MAX_AGE` per worker. |
| **05** | **Per-tenant cache isolation** | In-process policy cache, AST plan cache, and count cache serve tenant A's cached plans/counts to tenant B, or retain revoked permissions. | Key every in-process and Redis cache by `(tenant_id, user/policy_scope, version)`. Use a shared atomic version counter for instant multi-worker invalidation. |
| **06** | **Tenant migrations & provisioning** | A partial migration fan-out leaves schema drift; a half-created tenant is registered and serves runtime 500 errors. | Provide `migrate_tenants` command with per-tenant transaction locks. Provisioning sequence: `create` → `migrate` → `seed` → `register`, with automatic rollback and a `ready` status flag. |
| **07** | **Tenant-scoped files & control logs** | Uploads share a single flat storage directory. Pre-auth failures before tenant resolution have no tenant log to write to. | Namespace storage paths as `tenant/<tenant_id>/<module>/...`. Maintain a dedicated control-plane security log for pre-tenant events. |
| **08** | **Cross-tenant leak prevention** | A subtle routing bug or cross-tenant data leak is detected only in production. | Dedicated CI test suite: tenant A’s JWT token and entity IDs queried against tenant B’s endpoints must strictly return 403 Forbidden or 404 Not Found. |
| **09** | **Navigation modularity** | Core ships unused sidebar tables and mandatory seed steps, causing health check warnings on lean projects (like E-commerce). | Move navigation to an opt-in `modules/navigation` app. Exclude `seed_navigation` from the mandatory core seeding sequence. |
| **10** | **Field policy on filter, order & count** | A user without read access to `salary` can still filter or sort by it (`where salary > 50000`) and infer confidential values. | AST Query Compiler validates every filter, order-by, and join field against the role's field-level read policy, not just output serialization. |
| **11** | **Row scope (ABAC) choke point** | A prefetch relation, `COUNT(*)`, or domain service hook ORM call accidentally queries raw `Model.objects` and skips the row policy. | CRUD executors and domain services receive a policy-scoped QuerySet only, never raw `Model.objects`. Direct un-scoped manager access is banned. |
| **12** | **Mass assignment protection** | A client sets protected fields (`status`, `owner`, `id`, `is_superadmin`) during create or update requests. | Per-model write-field allowlists defined in `@register_model` and enforced universally in `SanitizationStage`. |
| **13** | **Core table API isolation** | A user inspects or mutates `AccessPolicy` or `AuditLog` records through generic populate CRUD. | Exclude core security models from generic CRUD registration or lock them exclusively to verified Superadmins. `AuditLog` is immutable (block update/delete). |
| **14** | **Default deny authorization** | A registered model with no policy or a policy lookup failure falls through to allow access. | Unregistered model returns HTTP 404; registered model with no explicit policy returns HTTP 403; policy load error fails closed to deny. |
| **15** | **Auth lifecycle & session hardening** | Downstream projects reimplement authentication with no lockout, token revocation, or refresh rotation. | Core `security/authn` provides token expiry, algorithm pinning (HS256/RS256), refresh token rotation, revocation blocklist, login rate-limiting, and CSRF defense. |
| **16** | **Throttling & query complexity caps** | A deep AST filter, a massive `$in` list, or an oversized payload exhausts worker threads and MySQL CPU. | Enforce per-user, IP, and tenant rate limits. Hard caps: AST depth ceiling of 5, max 100 `$in` elements, max 100 page limit, body size ceiling. |
| **17** | **Workflow & status write bypass** | A generic update writes directly to `status`, bypassing multi-stage approval workflows; a requester approves their own submission. | Direct status mutations are blocked on `has_workflow` models. Step actors are resolved server-side; strict separation of duties prevents self-approval. |
| **18** | **Webhook SSRF & safe queue payloads** | Outbound webhook URLs target internal IP ranges (`10.0.0.0/8`, `169.254.169.254`). Job queue payloads are deserialized unsafely. | Outbound guard blocks private/loopback/cloud-metadata IPs, re-checks after DNS resolution, enforces 5s timeouts. Queue payloads serialized strictly via JSON (no pickle). |
| **19** | **Upload safety & anti-decompression bomb** | Malicious uploads: zip bombs, SVG script execution (XSS), path traversal, or gigabyte image uploads. | `upload_guard`: checks file magic bytes, enforces `MAX_IMAGE_PIXELS` (prevents decompression bombs), 10MB size cap, bans SVGs with scripts, sanitizes filenames, strips EXIF. |
| **20** | **Client IP spoofing & request ID validation** | Forged `X-Forwarded-For` header poisons audit trails and bypasses IP throttles; crafted `X-Request-ID` injects CRLF log lines. | Strict `TRUSTED_PROXIES` setting to parse real client IP. Validates `X-Request-ID` format against alphanumeric/UUID regex (max 64 chars). |
| **21** | **Audit immutability & security event durability** | Audit records can be deleted/altered via ORM; async worker crash loses critical security events; 401/403 denials are not logged. | Override ORM `delete()` and `update()` on `AuditLog` to raise exceptions. Security events (401, 403, policy denials) use durable synchronous commits. |
| **22** | **Sanitization & double-logging prevention** | Only 5 keys are redacted; both `ApiAuditLogMiddleware` and Stage 10 log `/api/populate/`, duplicating audit records. | Pattern-based regex redaction with payload truncation. Requests are flagged with `_is_audited = True` to guarantee single-record deduplication. |
| **23** | **Response cache isolation & normalized errors** | A shared reverse proxy serves an authenticated response to another user; error responses leak SQL syntax or internal model names. | Authenticated responses emit `Cache-Control: private, no-store` and `Vary: Authorization`. Errors are sanitized into standard envelopes (never leak SQL). |
| **24** | **Custom downstream route security** | Custom views (login, binary exports, third-party webhooks) bypass Populate pipeline, skipping policy and audit checks. | Ship `PopulatePermission` DRF class and `@populate_secure` decorator so all custom endpoints inherit identical throttling, policy, and audit chains. |
| **25** | **Supply chain & version integrity** | Mutable Git tags change silently; downstream projects never receive security patches or run vulnerable dependencies. | Pin downstream installations to immutable Git commit SHAs, publish signed tags, mandate `pip-audit` in CI, maintain `SECURITY.md` with patch SLA. |
| **26** | **Boot-time configuration safety checks** | A production deploy running with `DEBUG=True`, empty `TRUSTED_PROXIES`, or missing DB router boots without error and runs insecurely. | Django system checks (`populate_core.checks`) validate environment at startup and refuse to boot if production security settings are violated. |
| **27** | **Single unified configuration surface** | Multiple conflicting settings (`POPULATE_CONFIG`, `POPULATE_ROLE_MODEL`, `POPULATE_SESSION_HANDLER`) cause security gaps. | Consolidate all configuration into a single, cohesive `POPULATE_CONFIG` dictionary, validated at boot time via a strict Pydantic schema. |

---

### Deep Implementation Blueprints for Core Subsystems

#### Group A: Multi-Tenant Data-Plane Isolation (Items 01–08)
1. **Strict Token-Bound Tenant Resolution (Anti-Replay Defense)**:
   ```python
   def resolve_tenant(request: HttpRequest) -> TenantContext:
       # Authenticated callers: Tenant is locked strictly to token 'tid' claim
       if request.user and request.user.is_authenticated:
           token_tid = getattr(request.user, "tenant_id", None)
           if not token_tid:
               raise SecurityViolationError("Authenticated token lacks mandatory 'tid' claim.")
           return TenantRegistry.get(token_tid)

       # Anonymous callers (public reads/creates): Resolve via subdomain or header
       header_tid = request.headers.get("X-Tenant-Id") or extract_subdomain(request.get_host())
       if not header_tid:
           raise TenantResolutionError("Tenant identifier required.")
       return TenantRegistry.get(header_tid)
   ```
2. **Fail-Closed Database Router**:
   ```python
   class TenantDatabaseRouter:
       def db_for_read(self, model, **hints):
           if model._meta.app_label in SHARED_APPS:
               return "default"
           tenant_db = get_current_tenant_db()
           if not tenant_db:
               raise TenantDatabaseUnboundError("Attempted DB access without active tenant binding.")
           return tenant_db
   ```
3. **Async Worker Tenant Re-Binding**:
   ```python
   # Using contextvars to propagate tenant binding into background thread pools
   tenant_ctx_var: ContextVar[str] = ContextVar("tenant_id", default="")

   def execute_in_worker(func, payload, tenant_id: str):
       def wrapped():
           token = tenant_ctx_var.set(tenant_id)
           try:
               return func(payload)
           finally:
               tenant_ctx_var.reset(token)
       thread_pool.submit(wrapped)
   ```

#### Group B: Security, ABAC & Model Choke Points (Items 10–14, 24)
1. **Universal Field Policy (Filters, Order-By, GroupBy & Metrics)**:
   The AST compiler checks fields against the role's forbidden list *before* generating SQL, preventing callers from inferring restricted data (e.g. grouping by `salary` or computing `SUM(salary)`):
   ```python
   def validate_field_access(field_name: str, policy: AccessPolicy):
       forbidden = policy.forbidden_fields.get("read", set())
       if field_name in forbidden:
           raise AuthorizationError(f"Field '{field_name}' is restricted by access policy.")

   # Applied universally:
   for node in ast_filter_nodes:
       validate_field_access(node.field_name, policy)
   for order_field in ordering_fields:
       validate_field_access(order_field.lstrip("-"), policy)
   for group_field in group_by_fields:
       validate_field_access(group_field, policy)
   for metric_name, expr in metrics_expressions.items():
       if isinstance(expr, dict) and "field" in expr:
           validate_field_access(expr["field"], policy)
   ```
2. **Policy-Scoped QuerySet Choke Point**:
   CRUD query builders and domain service hooks never access `Model.objects` directly:
   ```python
   # Enforce row-level ABAC scope at the root
   base_qs = PolicyEngine.get_scoped_queryset(request_context, model_cls)
   # Pass base_qs to services and executors
   ```
3. **Mass Assignment Allowlist**:
   ```python
   class ModelMetadata:
       write_allowlist: set[str] = {"name", "email", "phone"}
       immutable_fields: set[str] = {"id", "is_superadmin", "tenant_id", "created_at"}
   ```

#### Group C: Outbound Guards & Upload Safety (Items 18–19)
1. **SSRF Outbound Guard**:
   ```python
   BLOCKED_CIDRS = [
       ipaddress.ip_network("10.0.0.0/8"),
       ipaddress.ip_network("172.16.0.0/12"),
       ipaddress.ip_network("192.168.0.0/16"),
       ipaddress.ip_network("169.254.169.254/32"), # Cloud metadata
       ipaddress.ip_network("127.0.0.0/8"),
   ]

   def safe_outbound_request(url: str, data: dict, signature_key: str):
       parsed = urllib.parse.urlparse(url)
       resolved_ip = socket.gethostbyname(parsed.hostname)
       ip_obj = ipaddress.ip_address(resolved_ip)
       for blocked in BLOCKED_CIDRS:
           if ip_obj in blocked:
               raise SSRFSecurityError(f"Outbound destination {url} resolves to restricted IP.")
       # Post JSON payload with HMAC-SHA256 signature and 5s timeout
   ```
2. **Upload Decompression Bomb Guard**:
   ```python
   from PIL import Image
   Image.MAX_IMAGE_PIXELS = 25_000_000  # Cap at 25 Megapixels (prevents decompression bombs)
   ```

#### Group D: Boot-Time Safety Checks & Unified Config (Items 26–27)
```python
# populate_core/checks.py
@register(Tags.security)
def check_populate_production_settings(app_configs, **kwargs):
    errors = []
    if not settings.DEBUG:
        config = getattr(settings, "POPULATE_CONFIG", {})
        if not config.get("TRUSTED_PROXIES"):
            errors.append(Error("POPULATE_CONFIG['TRUSTED_PROXIES'] must be configured in production.", id="populate.E001"))
        if not config.get("ENFORCE_TENANT_ISOLATION"):
            errors.append(Error("Tenant isolation must be enabled in production environments.", id="populate.E002"))
    return errors
```

---

## 5.1 Security & Resource Exhaustion Controls (.env Driven Limits)

To prevent denial-of-service, runaway memory allocations, and database CPU starvation, the Populate Engine enforces hard limits on all dimensions of query execution. Every limit has a hardened production default and is fully overridable via `.env` so downstream projects can adjust limits declaratively:

### Resource Exhaustion Control Matrix

| Control Dimension | Threat / Why It's Security | Rule Enforced in Core | `.env` Variable & Production Default |
|---|---|---|---|
| **Max Page Size** | `limit=1000000` dumps whole tables or exhausts Python RAM. | `MAX_PAGE_LIMIT` is a hard ceiling. Values exceeding the cap are clamped or rejected with HTTP 422. Clients cannot raise it. | `POPULATE_MAX_PAGE_LIMIT=100` |
| **Offset Cap / Keyset Paging** | `offset=50,000,000` forces MySQL to scan and discard millions of rows. | Clamps max offset; deep pagination (>10,000) requires keyset/cursor pagination (`cursor=...`). | `POPULATE_MAX_OFFSET=10000` |
| **Count Query Cost** | `COUNT(*)` on large filtered tables pins MySQL CPU. | `want_count` is gated by the "Limit + 1" smart probe. Exact `COUNT(*)` has a 3s timeout and per-tenant/user caching. | `POPULATE_COUNT_TIMEOUT_MS=3000`<br>`POPULATE_COUNT_CACHE_TTL=60` |
| **Multi-Tier Rate Limiting** | Brute-force logins, data scraping, request flooding. | Tiered rate limiting per User, IP, Tenant, and Action. Strictest limits on auth (`/login/`) and mutation endpoints. | `POPULATE_RATE_LIMIT_ANON=60/min`<br>`POPULATE_RATE_LIMIT_USER=600/min`<br>`POPULATE_RATE_LIMIT_AUTH=5/min` |
| **AST Query Complexity** | Deeply nested ASTs, 50,000 `$in` elements, expensive `$contains` regex. | Hard ceiling on AST recursion depth, total AST node count, maximum `$in` list size, and prefetch join depth. | `POPULATE_MAX_AST_DEPTH=5`<br>`POPULATE_MAX_AST_NODES=25`<br>`POPULATE_MAX_IN_SIZE=100`<br>`POPULATE_MAX_PREFETCH_DEPTH=3` |
| **Per-Query Timeout** | One un-indexed slow query holds a worker thread and DB connection. | Injects MySQL query execution timeout comments (`/*+ MAX_EXECUTION_TIME(5000) */`) on all compiled QuerySets. | `POPULATE_QUERY_TIMEOUT_MS=5000` |
| **Body & Response Size** | Gigabyte JSON payloads or massive response envelopes crashing clients. | Rejects incoming request bodies exceeding ceiling; caps maximum serialized response rows per HTTP transaction. | `POPULATE_MAX_BODY_BYTES=10485760` (10MB)<br>`POPULATE_MAX_RESPONSE_ROWS=1000` |
| **Bulk Mutation & Export Limits** | One batch request attempts writing or exporting 100,000 rows. | Bulk CRUD operations clamped and processed in memory-safe chunks; exports are forced through the async queue. | `POPULATE_MAX_BULK_SIZE=1000`<br>`POPULATE_BULK_CHUNK_SIZE=250` |
| **Tenant Concurrency Ceiling** | One noisy or rogue tenant starves connection pools for all other tenants. | Per-tenant concurrent active request limit using an in-memory/Redis distributed semaphore. | `POPULATE_MAX_TENANT_CONCURRENCY=50` |
| **Upload File & Image Pixels** | Decompression bombs, gigabyte files, or disk exhaustion. | Enforces maximum upload byte size and Pillow `MAX_IMAGE_PIXELS` before decoding image buffers. | `POPULATE_MAX_UPLOAD_BYTES=10485760` (10MB)<br>`POPULATE_MAX_IMAGE_PIXELS=25000000` (25MP) |
| **Public Read Access Gate** | Unauthenticated callers access private data, or developers build redundant custom routers to expose company branding/settings. | `PUBLIC_READ_MODELS` permits unauthenticated `read` exclusively. Mutations return 401. Anonymous read sanitization strips private secrets automatically. | `POPULATE_PUBLIC_READ_MODELS=general_settings,company` |

---

### `.env` Integration & Default Template

Downstream projects simply place these variables in their local `.env` file to customize thresholds per environment (e.g. dev vs. high-load production):

```ini
# ==============================================================================
# DJANGO POPULATE CORE - DECLARATIVE MODEL POLICIES (.env)
# ==============================================================================
POPULATE_PUBLIC_READ_MODELS=general_settings,company
POPULATE_PUBLIC_CREATE_MODELS=lead,candidate,contact_inquiry
POPULATE_GLOBAL_MODELS=country,currency_master,system_plan
POPULATE_IMMUTABLE_MODELS=payment_journal,audit_log,asset_stock_ledger
POPULATE_READ_ONLY_MODELS=capability,sidebar,status_config
POPULATE_HIGH_FREQUENCY_MODELS=time_tracker_session,attendance_punch
POPULATE_RESTRICTED_EXPORT_MODELS=payroll,salary_structure,agent_token

# ==============================================================================
# DJANGO POPULATE CORE - RESOURCE & COMPLEXITY LIMITS (.env)
# ==============================================================================
POPULATE_MAX_PAGE_LIMIT=100
POPULATE_MAX_OFFSET=10000
POPULATE_MAX_AST_DEPTH=5
POPULATE_MAX_AST_NODES=25
POPULATE_MAX_IN_SIZE=100
POPULATE_MAX_PREFETCH_DEPTH=3
POPULATE_QUERY_TIMEOUT_MS=5000
POPULATE_COUNT_TIMEOUT_MS=3000
POPULATE_COUNT_CACHE_TTL=60
POPULATE_MAX_BODY_BYTES=10485760
POPULATE_MAX_RESPONSE_ROWS=1000
POPULATE_MAX_BULK_SIZE=1000
POPULATE_BULK_CHUNK_SIZE=250
POPULATE_MAX_TENANT_CONCURRENCY=50
POPULATE_MAX_UPLOAD_BYTES=10485760
POPULATE_MAX_IMAGE_PIXELS=25000000
POPULATE_RATE_LIMIT_ANON=60/min
POPULATE_RATE_LIMIT_USER=600/min
POPULATE_RATE_LIMIT_AUTH=5/min
```

---

## 5.2 Enterprise Operational Resilience & Cloud Production Guards

To guarantee seamless cloud deployment (Render, AWS, GCP, Kubernetes) and eliminate subtle runtime bugs over long-term operations, the Populate Engine incorporates 6 operational resilience guards:

### 1. Mutation Idempotency Guard (`X-Idempotency-Key`)
- **The Mobile & Network Flake Threat**: In mobile applications (`tracker_mobile` / Flutter) or spotty network connections, a user submitting a daily log, task, or approval may experience an HTTP timeout and retry. A shared key across different users or routes could return another user's cached response.
- **The Core Defense**:
  - The engine intercepts `X-Idempotency-Key: <uuid>` on all mutation requests (`create`, `update`, `delete`).
  - Cache Key: Strictly namespaced as `f"idempotency:{tenant_id}:{user_id}:{request.path}:{key}"` in Redis.
  - **Payload Hash Mismatch Detection**: Stores a SHA-256 hash of the request payload along with the response envelope. If a duplicate request arrives with the exact same key but a *different* payload, it rejects with `HTTP 422 Unprocessable Entity ("Idempotency key reused with mismatched payload.")`.
  - If identical, the cached response is returned immediately without re-executing service hooks or database writes.

### 2. Full Multilingual (Tamil/Indic Script) & 4-Byte Emoji Unicode Integrity
- **The Vernacular & Emoji Corruption Threat**:
  - In daily work tracking, team feeds, chat, and comments, employees frequently type in regional Indian languages like **Tamil (தமிழ்)**, Tanglish (mixed Tamil and English), or other Indic scripts, as well as modern 4-byte emojis (`🐛`, `🚀`, `✅`).
  - Standard MySQL 3-byte `utf8` cannot store 4-byte characters or complex multi-byte combining grapheme clusters (such as Tamil pulli / virama: க், த், ழ்; or vowel combinations: கி, தா, மி).
  - Writing native Tamil or emojis to a 3-byte table triggers `OperationalError 1366: "Incorrect string value..."` or silently corrupts the text into question marks (`??????`), destroying work logs and daily narrative history.
- **The Core Defense**:
  - **Universal `utf8mb4` Collation**: Mandates `utf8mb4_0900_ai_ci` (or `utf8mb4_unicode_520_ci` on older MySQL) across all database connections, database collations, and character columns.
  - **Combining Character & Diacritic Safety**: Preserves Tamil Unicode blocks (`U+0B80` to `U+0BFF`) without stripping combining vowel signs or consonants.
  - **Multilingual AST Search**: The AST Query Compiler supports case-insensitive and accent-aware substring searching (`$contains`, `$icontains`) across Tamil script without garbling text tokens.
  - **Boot-Time Collation Check**: Django system checks verify at startup that all active database tables and connections use 4-byte `utf8mb4`, refusing to boot in production if legacy 3-byte `utf8` is detected.

### 3. Centralized General Settings Architecture (Timezone, Location, Currency & Localization)
- **The Scattered Configuration & "Yesterday vs. Today" Trap**:
  - In many architectures, operational parameters are dangerously scattered: timezone in `.env`, currency hardcoded in service files, date formats copied across frontend components, and location/country buried in client tables.
  - If an employee in India (`UTC+05:30`) submits their daily status at 11:30 PM local time (which corresponds to 18:00 UTC), a naive UTC timestamp will categorize their work as happening "yesterday" in reports.
  - Similarly, calculating financial summaries, overtime shifts, or invoice totals without a centralized currency and fiscal year definition leads to multi-currency calculation drift.
- **The Core Architecture: Centralized `GeneralSettings` Singleton**:
  - The engine formalizes a centralized **`GeneralSettings`** model (or project-configurable `SETTINGS_PROVIDER`) serving as the Single Source of Truth for system-wide localization within each tenant database:
    ```python
    class GeneralSettings(models.Model):
        # Localization & Regional Settings
        timezone = models.CharField(max_length=64, default="Asia/Kolkata")  # IANA Timezone
        timezone_offset = models.IntegerField(default=330)                  # Minutes (+05:30)
        country_code = models.CharField(max_length=4, default="IN")          # ISO 3166-1 alpha-2
        currency = models.CharField(max_length=8, default="INR")             # ISO 4217
        currency_symbol = models.CharField(max_length=8, default="₹")
        date_format = models.CharField(max_length=32, default="YYYY-MM-DD")
        time_format = models.CharField(max_length=16, default="12h")         # 12h / 24h
        fiscal_year_start = models.PositiveSmallIntegerField(default=4)      # 4 = April (India)
        default_locale = models.CharField(max_length=16, default="ta-IN")     # Tamil / English
    ```
  - **In-Memory / Redis Singleton Caching**: Settings are cached under `f"settings:{tenant_id}"` with a 1-hour TTL. An `after_update` service hook automatically invalidates the cache upon modification, eliminating database read overhead on hot request paths.
  - **Automatic `RequestContext` Injection**: In Stage 3, the engine loads the cached settings and binds them to `request.context.settings`.
  - **`DateTimeNormalizer` Consumption**: When persisting domain dates (e.g., `reporting_date`, shift start/end) or compiling `$date` range queries, the engine converts UTC to the tenant's localized business calendar seamlessly.

### 4. Idle Connection Recycling & Session Timeout Enforcement
- **The Threat**: Cloud database load balancers (AWS RDS, Render) automatically sever idle TCP connections after `wait_timeout` (often 60–300 seconds). Furthermore, slow write locks or unindexed queries hold connections and freeze worker threads.
- **The Core Defense**: 
  - Sets `CONN_MAX_AGE = 60` and wraps connection acquisition with an active health ping (`connection.is_usable()`).
  - Sets connection-level session timeouts on handshake:
    ```sql
    SET SESSION max_execution_time = 5000;
    SET SESSION innodb_lock_wait_timeout = 5;
    ```
    This guarantees that both slow `SELECT` queries and blocked `UPDATE` row locks are terminated by MySQL within 5 seconds, freeing the worker thread.

### 5. Ephemeral Cloud Storage Portability (S3 / R2 / MinIO / Local)
- **The Container Wipe Threat**: On container platforms (Render, Heroku, ECS, Kubernetes), local container disk storage (`MEDIA_ROOT`) is ephemeral and is completely erased on every deploy or restart.
- **The Core Defense**: The engine's file and image upload subsystem abstracts storage via `POPULATE_STORAGE_BACKEND`. It supports `local`, `s3`, and `r2` (Cloudflare R2 / AWS S3) declaratively via environment variables without requiring code changes:
  ```ini
  POPULATE_STORAGE_BACKEND=s3 # or local / r2
  POPULATE_S3_BUCKET_NAME=my-company-assets
  POPULATE_S3_REGION=us-east-1
  ```

### 6. Audit Log Retention & Automatic Partition Archival (`archive_audit_logs`)
- **The 10M Row Database Drag**: Because every mutation is immutably audited, an active deployment will accumulate 2,000,000+ audit rows per year. Over time, an un-partitioned table slows down MySQL backups and index maintenance.
- **The Core Defense**:
  - The engine's `AuditLog` model is designed to support MySQL native RANGE partitioning on `created_at` (monthly partitions).
  - Ships an automated management command:
    ```bash
    python manage.py archive_audit_logs --older-than=90d --export-to-s3
    ```
    This exports older audit partitions to compressed S3/cold storage and drops expired partitions in `O(1)` time without locking active tables.

### 7. Configurable Public Read Access & Zero-Custom-Router Architecture (`PUBLIC_READ_MODELS`)
- **The Redundant Router Trap & Secret Leak Threat**:
  - Developers build redundant custom routers to expose company branding or public catalogs before login.
  - Furthermore, if stripping relies solely on ad-hoc service hooks, a newly added private column (e.g. `api_secret`, `tax_id`) in a public model could silently leak to anonymous callers.
- **The Core Defense**:
  - `django-populate-core` exposes `PUBLIC_READ_MODELS` configurable via `settings.POPULATE_CONFIG['PUBLIC_READ_MODELS']` or `.env`.
  - **Explicit `public_fields` Allowlist**: Every public model declares an explicit allowlist:
    ```python
    @register_model("company", public_fields=["name", "logo_url", "primary_color", "support_email"])
    class Company(models.Model):
        ...
    ```
  - **Fail-Safe Projection**: In Stage 6, anonymous read responses are clamped strictly to `public_fields`. Any column not in the allowlist is stripped by default.
  - **Mutations Strictly Blocked**: `create`, `update`, and `delete` on public models strictly require authenticated admin tokens (HTTP 401).

### 8. Export Security & Anti-Formula Injection Guard
- **The Threat**: Exporting un-sanitized user strings to Excel/CSV allows attackers to inject spreadsheet formulas (`=cmd|' /C calc'!A0`, `+`, `-`, `@`) that execute arbitrary code when opened by accountants or managers (CSV Formula Injection). Furthermore, hardcoding `is_superadmin` prevents delegation.
- **The Core Defense**:
  - **Export as a Formal Policy Action**: Handled via standard policy permission `can_export` rather than hardcoded string role matching.
  - **Formula Prefixing**: In Stage 9, any string cell starting with `=`, `+`, `-`, or `@` is automatically prefixed with a single quote `'` (or tab character), neutralizing formula execution across Microsoft Excel, Google Sheets, and LibreOffice.
  - **Signed Secure Download Links**: Exports generate signed, short-lived URLs bound strictly to `(tenant_id, user_id)` with a 15-minute expiry.

### 9. Global Master Data Security (`GLOBAL_MODELS` Write-Lock)
- **The Threat**: Shared master tables (`countries`, `currencies`, `subscription_plans`) are accessible across all tenants. A malicious or careless tenant administrator updating a country or currency could mutate shared master data for all other companies on the platform.
- **The Core Defense**:
  - `GLOBAL_MODELS` are strictly **read-only** for all tenant-scoped users and standard populate endpoints.
  - Mutations (`create`, `update`, `delete`) on global models are rejected with `HTTP 403 Forbidden` unless the request originates from the verified central control-plane SuperAdmin interface.

### 10. Strict Configuration Precedence Hierarchy
- **The Conflict Threat**: When limits and flags can be declared in `@register_model`, `POPULATE_CONFIG`, and `.env`, conflicting values create confusion over which rule takes effect.
- **The Core Defense**:
  - The engine resolves all configuration using a strict, unambiguous precedence order:
    $$\text{Model Decorator} > \text{POPULATE\_CONFIG (settings.py)} > \text{.env} > \text{Package Defaults}$$
  - **Core Model Exemption**: Core security models (`AccessPolicy`, `AuditLog`, `GeneralSettings`) are hard-coded as immutable within the kernel; they cannot be inadvertently overridden or exposed to public CRUD.

---

## 5.3 Systemic Crash-Proofing, Blast Radius Containment & Safe Failure Architecture
*(The "Anti-Server-Crash" Shield)*

A system that does not know how to handle unexpected failures is itself a failure. In production, users will do unpredictable things, attackers will exploit computational bottlenecks, and third-party APIs will go down.

The Populate Engine incorporates a **7-layer Crash-Proofing Shield** ensuring that unpredictable user actions or malicious payloads can **never crash the server process, exhaust CPU/memory, or cause container restarts**:

### 1. Computational DoS & Bcrypt Exhaustion Defense (The 128-Character Password Ceiling)
- **The Threat**: An attacker sends a 10MB string as the `password` in `/api/auth/login/`. Bcrypt hashing a 10MB string consumes 100% of a CPU core for several minutes. Sending 10 concurrent requests freezes all Gunicorn/Uvicorn worker threads, causing health checks to fail and cloud platforms (Render, AWS) to restart the container in a crash loop.
- **The Defense**: `pre_validation_guard`:
  - Enforces an immediate $O(1)$ length check at the very first byte of ingress: passwords are capped at **maximum 128 characters** (`max_length=128`).
  - Text fields in AST query filters are capped at 5,000 characters before regex compilation or hashing.
  - Payloads violating these caps are rejected with `HTTP 400 Bad Request` in `<0.01ms`, completely neutralizing CPU exhaustion before compute-heavy hashing or regex starts.

### 2. The 3-Tier "Blast Radius Containment" & Universal Try-Catch Absorber
- **The Threat**: An unexpected user payload triggers an unhandled `TypeError`, `KeyError`, or `ZeroDivisionError` inside a service hook or query builder. Swallowing hook failures blindly allows corrupt data to save (fail-open), while unhandled exceptions in raw Django crash worker threads and leak database schemas.
- **The Defense**: Three concentric protective boundaries isolate every failure:
  - **Tier 1 (Service Hook Integrity - Fail Closed for `before_*`)**: 
    - `before_create`, `before_update`, and `before_delete` hooks **STRICTLY FAIL CLOSED**. If validation, permission checks, or calculations fail in a `before_*` hook, the transaction is **immediately aborted and rolled back**. Invalid data is never persisted.
    - `after_create`, `after_update`, and `after_delete` side effects (FCM push, emails, external webhooks) execute strictly via **`transaction.on_commit(...)`** *after* the database write is safely committed. Side-effect exceptions are caught, logged to `error_logs`, and isolated so third-party network flakes never roll back durable business transactions.
  - **Tier 2 (Pipeline Stage Rollback)**: If an error or database constraint fails in any pipeline stage, the active database transaction is rolled back cleanly (`transaction.set_rollback(True)`), preventing dirty or partial database writes.
  - **Tier 3 (Global Crash Absorber & Sanitized Error Logging)**: `PopulateExceptionHandler` intercepts any unhandled `Exception`:
    - Generates an immutable incident reference: `ref = f"ERR-{uuid4().hex[:8].upper()}"`.
    - **Credential Sanitization Before Logging**: All request context dictionaries (headers, body, query parameters) are passed through `sanitize_credentials(...)` to scrub passwords, Bearer tokens, and secrets *before* writing the traceback to `ErrorLog`.
    - **Control DB Fallback for Unbound Tenant Errors**: If the error occurred before tenant resolution (or tenant database is unreachable), the incident is written to the central control-plane database, ensuring pre-auth errors are never lost.
    - Returns a clean, human-readable response without crashing the worker process:
      ```json
      {
        "success": false,
        "code": "INTERNAL_SERVER_ERROR",
        "ref": "ERR-9F8A2B14",
        "message": "An unexpected error occurred. The incident has been recorded with reference ERR-9F8A2B14."
      }
      ```
    - The Python process and worker threads remain 100% healthy.

### 3. Out-of-Memory (OOM) Protection & Ingress Payload Caps
- **The Threat**: A user requests 1,000,000 rows or an attacker uploads a "decompression bomb" (e.g. a 2MB compressed image that decompresses into a 20,000x20,000 pixel, 1.2GB bitmap in RAM), triggering the Linux OOM Killer (`SIGKILL`) to terminate the backend container.
- **The Defense**:
  - `DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760` (10MB hard ceiling at the HTTP ingress before buffering into RAM).
  - Pillow `Image.MAX_IMAGE_PIXELS = 25000000` (25 megapixels max). Images exceeding 25MP are rejected before decompression.
  - QuerySet Streaming: Data exports and queries stream row-by-row with `QuerySet.iterator(chunk_size=1000)` instead of loading entire tables into Python RAM.

### 4. Database Worker Freeze Prevention (Per-Query Kill Switch)
- **The Threat**: An un-indexed query on a 5,000,000-row table locks a MySQL connection for 60 seconds. When 20 users trigger this query, all 20 worker threads freeze waiting for MySQL. Health checks (`/api/test/`) time out, and load balancers restart the server.
- **The Defense**:
  - The AST Query Compiler injects a strict execution timeout comment on every compiled query:
    `/*+ MAX_EXECUTION_TIME(5000) */` (5,000ms).
  - If a query takes longer than 5 seconds, MySQL terminates the query automatically with `ER_QUERY_TIMEOUT`. The worker catches this, logs a slow-query alert, and returns `HTTP 504 Gateway Timeout` to the caller. The worker thread is freed in 5s instead of hanging indefinitely.

### 5. JSON Malformed & Recursive Bomb Defense
- **The Threat**: An attacker sends deeply nested JSON (`{"a": {"a": {"a": ... 5000 levels}}}`) designed to crash Python with `RecursionError: maximum recursion depth exceeded`.
- **The Defense**: The Ingress Parser enforces an AST recursion depth ceiling of 10 levels. If JSON nesting depth exceeds 10, parsing halts immediately and returns `HTTP 422 Unprocessable Entity` before recursion can threaten Python call stacks.

### 6. Third-Party API Circuit Breaker (Anti-Cascading Outage)
- **The Threat**: A service hook calls an external API (Firebase FCM, Razorpay, SMS gateway). If that third party hangs or goes down for 30 seconds, every incoming Populate request freezes waiting for network I/O.
- **The Defense**:
  - **Mandatory Async Queue Offload**: All external network I/O is offloaded to the async worker pool (`JobQueue.dispatch_async`) rather than running on the request-response thread.
  - **Circuit Breaker**: If 5 consecutive outbound network calls fail, the circuit trips open for 60 seconds, failing fast in `<1ms` without holding worker threads.

### 7. Process Recycling & Anti-Memory Leak Guard
- **The Threat**: Python garbage collection and C-extensions gradually leak memory over days of continuous high-volume operation until container memory is exhausted.
- **The Defense**: Gunicorn is configured with `--max-requests 1000 --max-requests-jitter 50`. Each worker process gracefully terminates and respawns after handling 1,000 requests, releasing all memory back to the OS without dropping active HTTP connections.

### 8. Distributed Rate-Limiting & Production Redis Mandatory Check
- **The Threat**: When rate limits and semaphores rely on local in-memory counters, running a multi-process WSGI server (e.g. 8 Gunicorn workers) multiplies the allowed limit by 8x. An attacker can distribute requests across workers and bypass throttles.
- **The Defense**:
  - All rate-limiting buckets and tenant concurrency semaphores are backed strictly by Redis via atomic Lua scripts.
  - System Boot Check (`populate_core.checks`): Django system checks verify at boot time that `CACHES['default']['BACKEND']` is configured with a distributed Redis backend (e.g. `django_redis.cache.RedisCache`) whenever `DEBUG = False`. The server strictly refuses to boot in production if an in-memory or dummy cache is detected.

---

## 6. Phased Roadmap to Build & Release `django-populate-core`

### Phase A: Extraction & Decoupling from `E-commerce`
- [ ] Create dedicated workspace / Git repository for `django-populate-core`.
- [ ] Copy `D:\Axinix Projects\E-commerce\backend\core` into the new repo under `populate_core/`.
- [ ] Decouple `models.py`:
  - Parameterize `AccessPolicy.role` to use `POPULATE_CONFIG['ROLE_MODEL']`.
  - Use `settings.AUTH_USER_MODEL` for `AuditLog.user`.
- [ ] Decouple `create.py`, `update.py`, `delete.py`:
  - Eliminate hardcoded `RESTRICTED_..._MODELS` sets.
  - Implement declarative model flags: `allow_direct_create`, `allow_direct_update`, `allow_direct_delete`, `table_type="ledger"`.
- [ ] Purge ecommerce-specific management commands (`seed_areas`, `seed_geography`, etc.).
- [ ] Cleanse `phone.py` and `authentication.py` of any `catalogue` imports.

### Phase B: Packaging & Configuration Layer
- [ ] Implement `populate_core/conf.py` to provide safe defaults with downstream override capability.
- [ ] Create `pyproject.toml` and `setup.cfg` defining package metadata, entrypoints, and dependencies.
- [ ] Build `populate_core/management/commands/init_populate.py` (CLI scaffolding command).

### Phase C: Self-Contained Test Suite
- [ ] Create `tests/test_settings.py` and `tests/runtests.py`.
- [ ] Implement standalone unit tests verifying:
  - 10-stage execution pipeline.
  - AST Query compiler (filters, operators, sorting, pagination).
  - RBAC / ABAC policy evaluator.
  - Audit logging and middleware.
- [ ] Ensure all tests pass in complete isolation from any external app.

### Phase D: Git Repository Release (`v1.0.0`)
- [ ] Push to dedicated Git repository (e.g., `github.com/<org>/django-populate-core`).
- [ ] Create GitHub Release and tag `v1.0.0`.
- [ ] Document quickstart and API in `README.md`.

### Phase E: Downstream Consumption in `tracker-v2` & `E-commerce`
- [ ] In `tracker-v2`: Add `django-populate-core @ git+https://...` to `requirements.txt`.
- [ ] Verify that `tracker-v2` imports `populate_core` and boots up cleanly without local core duplication.
- [ ] In `E-commerce`: Replace local `backend/core` with the standalone package dependency to unify the codebase across all projects.

---

## 7. Living Status & Next Steps

| Milestone | Deliverable | Status |
|---|---|---|
| **Specification** | `STANDALONE_DJANGO_POPULATE_PACKAGE_PLAN.md` | `COMPLETED` |
| **New Repo Setup** | Initialize `django-populate-core` git repository | `READY_FOR_CREATION` |
| **Decoupling** | Purge domain leaks & implement configurable settings | `PENDING` |
| **Release v1.0.0** | Tag release on Git | `PENDING` |
| **Tracker Integration** | Install in `tracker-v2` and begin Domain/BRS Phase | `PENDING` |
