# Workhub Tracker: Backend Migration to Python Django + MySQL (Populate Engine)
## Master Architecture & Phase-by-Phase Implementation Plan

> **Document Status**: Living Architectural Roadmap & Progress Tracker  
> **Source Engine**: `D:\Axinix Projects\E-commerce\backend\core`  
> **Target Base**: Workhub Tracker (`tracker-v2`)  
> **Next Immediate Milestone**: Complete Core Engine Migration (Django + MySQL)  
> **Subsequent Feature Milestone**: Implement AI-Powered Daily Work Status and Reporting System (`docs/BRS_AI_Daily_Work_Status_System.docx`)

---

## 1. Executive Summary & Strategy

The current backend for `tracker-v2` runs on **Node.js/Express + MongoDB**. To achieve unified enterprise performance, transactional consistency, relational integrity, and cross-platform synergy, the backend architecture is transitioning to **Python 3.12+ / Django + MySQL**.

Rather than rebuilding backend infrastructure from scratch, this migration ports the battle-tested, high-performance **Populate Engine** directly from `D:\Axinix Projects\E-commerce\backend\core`. 

### The Master Sequence:
1. **First**: Complete the entire backend core transition (Django + MySQL + 10-Stage Populate Pipeline + Auth/RBAC + Audit Logging).
2. **Verify**: Ensure the core engine passes all integrity and pipeline verification tests with 100% compliance.
3. **Then (New Planning Phase)**: Plan and execute the domain models and AI extraction pipeline for the **AI-Powered Daily Work Status and Reporting System** (`docs/BRS_AI_Daily_Work_Status_System.docx`).

> [!TIP]
> **STANDALONE REUSABLE PACKAGE SPECIFICATION**:  
> To enable cross-project reuse via Git install (`pip install git+https://...`), the core Populate Engine is being packaged as an independent zero-leakage repository. See full architecture and decoupling details in [`docs/STANDALONE_DJANGO_POPULATE_PACKAGE_PLAN.md`](file:///d:/Axinix%20Projects/tracker-v2/docs/STANDALONE_DJANGO_POPULATE_PACKAGE_PLAN.md).

---

## 2. Core Architecture Mapping

| Layer | Existing (Node.js + MongoDB) | Target (Python/Django + MySQL) | Source in `E-commerce` |
|---|---|---|---|
| **Entry Point** | `/api/populate/:action/:model` | `/api/populate/<action>/<model>` | `core/urls.py`, `core/views.py` (`PopulateAPIView`) |
| **Pipeline Engine** | `populateHelper.js` | 10-Stage `PopulatePipeline` | `core/pipeline/executor.py`, `stages.py` |
| **Telemetry & Metrics** | Ad-hoc console timers | `PipelineObserver` (stage-by-stage latency) | `core/pipeline/observer.py` |
| **Access Control (ABAC/RBAC)** | `policyEngine.js` | `core.policy` (`evaluator.py`, `abac.py`) | `core/policy/`, `core/models.py` (`AccessPolicy`) |
| **Model Registry** | Mongoose `models/` folder | `@register_model` declarative registry | `core/registry/model_registry.py` |
| **Service Registry & Hooks** | `services/<model>.js` | `BaseService` lifecycle hooks (`before_create`, etc.) | `core/registry/service_registry.py` |
| **Query Compilation** | `buildReadQuery.js` | AST Query Compiler (`compiler.py`, `relation_resolver.py`) | `core/query/` |
| **Security & Guards** | Custom regex / string slicing | `lookup_guard.py`, `identifier_guard.py`, `sanitizer.py` | `core/security/` |
| **Data Validation** | Joi / Mongoose schemas | `validator.py`, `rules.py`, `schemas/base.py` | `core/validation/` |
| **Audit Logging** | In-app logs / mongo collections | `AuditLogger` + `ApiAuditLogMiddleware` (`audit_logs` table) | `core/audit/` |
| **Authentication & Users** | Custom JWT middleware | `users` Django app (`User`, `Role`, `UserSession`, `LoginView`) | `users/` |

---

## 2.1 Knowledge Brain Parity Matrix: `knowledge_brain/Core/POPULATE_ENGINE.md`

Every architectural invariant, security gate, and operational constraint defined in [`knowledge_brain/Core/POPULATE_ENGINE.md`](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Core/POPULATE_ENGINE.md) has been audited and mapped directly to the Python/Django Populate Engine:

| `POPULATE_ENGINE.md` Concept | Node.js / MongoDB Behavior | Django + MySQL Architecture (`django-populate-core`) | Parity Status |
|---|---|---|---|
| **1. The Single Route Gate** | `populateRoutes.js` (`/api/populate/:action/:model/:id`) | `core/urls.py` (`/api/populate/<action>/<model_name>/[<object_id>]`) | ✅ **100% Parity** |
| **2. Canonical Model Mapping** | `CANONICAL_MODEL_NAMES` (normalizes `ticket`, `tickets`, `Ticket`) | `ModelRegistry._aliases` (supports singular, plural, and custom aliases via `@register_model(..., aliases=['tickets'])`) | ✅ **100% Parity** |
| **3. Multi-Tenant Data Isolation** | MongoDB Database-per-tenant (`TenantConnectionManager`, `AsyncLocalStorage`) | Configurable Multi-Tenancy: Row-level tenant isolation via AST Query Scoping (`tenant_id` injection) or Dynamic Multi-DB Routing (`using(tenant_db)`) | ✅ **100% Parity** (Configurable) |
| **4. Module Entitlement Gate** | `moduleGateMiddleware.js` (rejection with HTTP 403 `MODULE_LICENSE_REQUIRED` if unlicensed) | Integrated Pipeline Stage 04: checks `RequestContext.tenant_context['enabled_modules']` against model's `module_key`. Fails closed with `ModuleLicenseError` (HTTP 403) | ✅ **100% Parity** (Integrated into Stage 04) |
| **5. Dynamic Policy & FBAC** | `policyEngine.js` + FBAC (`isSelf`, `isManager`) | `core/policy/engine.py` + `conditions/` (`is_owner`, `is_manager`, `matches_attribute`, and custom condition callables) | ✅ **100% Parity** |
| **6. Zero Static Model Imports** | Models dynamically resolved from tenant proxy (`Collection.js`) | Models registered dynamically in `ModelRegistry` and resolved via `ModelRegistry.get(model_name)`. Services consume registry contracts | ✅ **100% Parity** |
| **7. Service Lifecycle Hooks** | `beforeCreate`, `afterCreate`, `beforeUpdate`, `afterUpdate`, `beforeDelete`, `afterDelete` in `services/<model>.js` | `before_create`, `after_create`, `before_update`, `after_update`, `before_delete`, `after_delete` in `BaseService` (`services/<model>_service.py`) | ✅ **100% Parity** |
| **8. Fail-Closed Aggregation & Guard** | `safeAggregator.js` (enforces stage limits on `$lookup`, `$unwind`) | `PlanningStage` enforces `MAX_PREFETCH_DEPTH = 3` and `CHILD_PAGINATION_CEILING = 50` on relational joins; rejects unbounded deep queries | ✅ **100% Parity** (Rule 9 Safeguard) |
| **9. Flat Populate & Path Collision Guard** | `sanitizeRead.js` collapses parent/child conflicts before projection | `compiler.py` and `output.py` automatically handle Django relational projection and relation trees without column collisions | ✅ **100% Parity** |
| **10. Concurrency & DB Lock Windows** | `requestQueue.js` & `raceConditionHandler.js` | Django `transaction.atomic()` + `select_for_update()` with strict `<10ms` lock window rule (Rule 9 limitation recipe) | ✅ **100% Parity** |
| **11. Request Tracing & Correlation** | `requestTracer.js` assigns `req.id` | `ApiAuditLogMiddleware` extracts / generates `X-Request-ID` and binds it across all 10 stages in `RequestContext.request_id` | ✅ **100% Parity** |
| **12. Immutable Audit Logging** | `auditLogger.js` logs mutations to MongoDB | Stage 10 `FinalizationStage` commits immutable records to MySQL `audit_logs` table asynchronously (non-blocking background worker, zero response stalling) | ✅ **100% Parity** |

---

## 3. The 10-Stage Populate Pipeline Blueprint

Every request entering `/api/populate/:action/:model` flows through the immutable 10-stage pipeline:

```
[HTTP Request] -> /api/populate/<action>/<model_name>/<object_id>
       │
       ▼
 [01. INGRESS]       ──> Parse HTTP request, headers, correlation ID, query params -> RequestContext
       │
       ▼
 [02. VALIDATION]    ──> Validate action, registered model, schema payload shape
       │
       ▼
 [03. SANITIZATION]  ──> Enforce identifier guards, protect against SQLi / illegal lookup operators
       │
       ▼
 [04. AUTHORIZATION] ──> Role-based & Attribute-based policy check (Superadmin boolean bypasses cleanly)
       │
       ▼
 [05. PARSING]       ──> Developer DSL -> AST (Abstract Syntax Tree)
       │
       ▼
 [06. PLANNING]      ──> Analyze joins, select_related & prefetch_related optimization (depth ceiling: 3)
       │
       ▼
 [07. COMPILATION]   ──> Compile AST into optimized Django QuerySet
       │
       ▼
 [08. EXECUTION]     ──> Execute CRUD under minimal DB lock windows (<10ms) & fire domain Service Hooks
       │
       ▼
 [09. SERIALIZATION] ──> Enforce field-level projection, allow/forbidden gates & type conversion
       │
       ▼
 [10. FINALIZATION]  ──> Return `{ success: true, data, count }` instantly & dispatch non-blocking async audit log to MySQL
```

---

## 4. Phase-by-Phase Implementation Plan

### Phase 1: Environment & Django Scaffold
*Establish the Python virtual environment, Django 6.x framework, MySQL client, and core configurations.*

- [ ] **Task 1.1**: Create backend directory structure (`backend_django/` or target `backend/`).
- [ ] **Task 1.2**: Set up Python virtual environment (`python -m venv myenv`) and configure `requirements.txt`:
  - `Django>=6.1.1`
  - `djangorestframework>=3.18.1`
  - `django-cors-headers>=4.9.0`
  - `mysqlclient>=2.3.0`
  - `python-dotenv>=1.2.3`
  - `bcrypt>=5.0.0`
  - `Pillow>=12.3.0`
  - `pydantic>=2.13.5`
  - `sqlparse>=0.6.0`
  - `asgiref>=3.12.1`
  - `openpyxl>=3.1.5`
- [ ] **Task 1.3**: Configure `config/settings.py`:
  - MySQL database configuration with strict 4-byte `utf8mb4` encoding and `utf8mb4_0900_ai_ci` collation:
    - Full support for Tamil (தமிழ்), Tanglish, and Indic scripts (`U+0B80`–`U+0BFF`) with combining grapheme clusters (pulli virama, vowel markers) and 4-byte emojis (`🐛`, `🚀`).
    - Enforce `ROW_FORMAT=DYNAMIC` for InnoDB tables to eliminate index key length limits (767-byte trap on `VARCHAR(255)`).
    - Database `OPTIONS`: `charset='utf8mb4'`, `init_command="SET NAMES 'utf8mb4' COLLATE 'utf8mb4_0900_ai_ci', sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'"`.
    - JSON response serialization with `ensure_ascii=False` to preserve native Tamil text in API responses and logs.
  - CORS settings for React Web (`http://localhost:5173`) and Flutter mobile app.
  - DRF configuration and custom exception handling.
  - Custom `AUTH_USER_MODEL = 'users.User'`.
  - Installed apps: `corsheaders`, `rest_framework`, `core`, `users`, `services`.
- [ ] **Task 1.4**: Configure `config/urls.py`, `manage.py`, and root health check `/api/test/`.
- [ ] **Task 1.5**: Create environment file template (`.env.example` and `.env`).

#### Acceptance Criteria for Phase 1:
- [ ] `python manage.py check` executes without warnings or errors.
- [ ] `python manage.py runserver` starts successfully and returns `{ "status": "healthy" }` on `GET /api/test/`.
- [ ] Django connects cleanly to local/remote MySQL instance.

---

### Phase 2: Core Populate Engine Port (From `E-commerce`)
*Copy, adapt, and integrate the full 10-stage Populate Engine and system models.*

- [ ] **Task 2.1: Registry Subsystem (`core/registry/`)**:
  - [ ] Port `model_registry.py` (`@register_model` decorator, table types, aliases).
  - [ ] Port `service_registry.py` (`BaseService`, `@register_service`, hook lifecycle).
  - [ ] Port `policy_registry.py` & `relation_registry.py`.
- [ ] **Task 2.2: Security Subsystem (`core/security/`)**:
  - [ ] Port `authentication.py` (bearer token & session authentication).
  - [ ] Port `identifier_guard.py` (validates field names against injection).
  - [ ] Port `lookup_guard.py` (whitelists valid Django lookup operators).
  - [ ] Port `sanitizer.py` (recursive sanitization of read, write, and update payloads).
- [ ] **Task 2.3: Validation Subsystem (`core/validation/`)**:
  - [ ] Port `validator.py`, `rules.py`, and `schemas/base.py`.
- [ ] **Task 2.4: Policy & ABAC Subsystem (`core/policy/`)**:
  - [ ] Port `evaluator.py` (evaluates permissions, field allow/forbidden sets, and `PUBLIC_READ_MODELS` bypass for unauthenticated reads).
  - [ ] Port `abac.py` (dynamic condition evaluation).
- [ ] **Task 2.5: Query Compilation Subsystem (`core/query/`)**:
  - [ ] Port `ast.py` (Abstract Syntax Tree node representations).
  - [ ] Port `filters.py` (filter AST parsing).
  - [ ] Port `relation_resolver.py` (automated join and foreign key mapping).
  - [ ] Port `builder.py` (DSL to QuerySet builder).
  - [ ] Port `compiler.py` (compilation into executable queries).
- [ ] **Task 2.6: Pipeline Subsystem (`core/pipeline/`)**:
  - [ ] Port `context.py` (`RequestContext` container).
  - [ ] Port `observer.py` (`PipelineObserver` latency and stage telemetry).
  - [ ] Port `stages.py` (10 stages implementation, Stage 4 handling `PUBLIC_READ_MODELS`).
  - [ ] Port `executor.py` (`PopulatePipeline.execute`).
- [ ] **Task 2.7: CRUD & Serialization Subsystem**:
  - [ ] Port `core/crud/` (`create.py`, `read.py`, `update.py`, `delete.py`).
  - [ ] Port `core/serialization/` (`base.py`, `output.py` with anonymous sensitive field stripping).
  - [ ] Port `core/response/` (`normalizer.py`, `exceptions.py`, crash-proofing exception handler with unique incident reference and zero unhandled server crashes).
- [ ] **Task 2.8: Audit Subsystem (`core/audit/`)**:
  - [ ] Port `logger.py` (`AuditLogger`).
  - [ ] Port `helpers.py` (`record_audit_log`, `sanitize_payload`).
  - [ ] Port `middleware.py` (`ApiAuditLogMiddleware` for automatic `X-Request-ID` and non-populate auditing).
- [ ] **Task 2.9: Core Models (`core/models.py`)**:
  - [ ] `GeneralSettings`: Centralized localization singleton (timezone, currency, country, date/time format, fiscal year start) with Redis caching and automatic `RequestContext` injection.
  - [ ] `Capability`: UI & business gate registry.
  - [ ] `Sidebar`: Dynamic navigation tree with permission gates.
  - [ ] `AccessPolicy`: Dynamic RBAC/ABAC policy storage per role & model.
  - [ ] `AuditLog`: Immutable audit trail with `request_id`, user, path, IP, before/after states.
- [ ] **Task 2.10: Core Routing & Views**:
  - [ ] Port `core/views.py` (`PopulateAPIView` with `permission_classes` supporting `PUBLIC_READ_MODELS` unauthenticated read access).
  - [ ] Port `core/urls.py` (`/api/populate/<action>/<model_name>/[<object_id>]`).

#### Acceptance Criteria for Phase 2:
- [ ] `python manage.py makemigrations core` generates migration file without syntax errors.
- [ ] `python manage.py migrate core` successfully creates `general_settings`, `capabilities`, `access_policies`, and `audit_logs` tables in MySQL.
- [ ] Model registry initializes and registers core models on Django app ready.

---

### Phase 3: Identity, Auth & User Management App (`users`)
*Establish custom user, role master, session management, and authentication endpoints.*

- [ ] **Task 3.1: User & Role Models (`users/models.py`)**:
  - [ ] `Role`: stores `name`, `is_superadmin` (boolean), `status` (1=Active, 0=Inactive), timestamps.
  - [ ] `User`: extends `AbstractUser`, includes `role` (FK to Role), `phone`, address details, `status`.
  - [ ] `UserSession`: tracks active login sessions, device details, IP, expiry.
- [ ] **Task 3.2: Auth Endpoints & Views (`users/views.py`, `users/urls.py`)**:
  - [ ] `POST /api/auth/login/`: Validates credentials, issues session token / JWT, records login audit.
  - [ ] `GET /api/auth/me/`: Returns authenticated user profile, role, and capabilities.
  - [ ] `POST /api/auth/logout/`: Invalidates user session cleanly.
- [ ] **Task 3.3: Authentication Backend (`users/backends.py`)**:
  - [ ] Multi-field authentication supporting login by username, email, or phone.
- [ ] **Task 3.4: Seeding Script (`users/management/commands/seed_admin.py`)**:
  - [ ] Seeds default Super Admin role (`is_superadmin=True`).
  - [ ] Seeds default Administrator account.
  - [ ] Seeds standard baseline roles (e.g., Manager, Team Member).

#### Acceptance Criteria for Phase 3:
- [ ] `python manage.py makemigrations users && python manage.py migrate users` completes cleanly.
- [ ] `python manage.py seed_admin` creates Super Admin role and user in MySQL.
- [ ] `POST /api/auth/login/` authenticates and returns user details and authorization tokens.
- [ ] `GET /api/auth/me/` returns the authenticated identity.

---

### Phase 4: Populate Pipeline Core Verification & Test Suite
*Port and run rigorous test suites to ensure 10-stage execution compliance, security gates, and audit trails.*

- [ ] **Task 4.1**: Port `tests_phase1_integrity.py` and `tests_phase2_integrity.py` from `E-commerce/backend/core`.
- [ ] **Task 4.2**: Test Superadmin policy bypass:
  - Verify that a user with `is_superadmin=True` bypasses policy checks cleanly without string heuristics.
- [ ] **Task 4.3**: Test standard user ABAC enforcement:
  - Create non-admin role with an `AccessPolicy`.
  - Verify `read`, `create`, `update`, `delete` permissions are respected.
  - Verify forbidden fields are stripped from responses by `SerializationStage`.
- [ ] **Task 4.4**: Test CRUD operations via `/api/populate/`:
  - `POST /api/populate/create/users`
  - `POST /api/populate/read/users` (with AST filters, sorting, pagination)
  - `POST /api/populate/update/users/<id>`
  - `POST /api/populate/delete/users/<id>` (soft-delete enforcement with status=0)
- [ ] **Task 4.5**: Test Audit Logging:
  - Verify that every operation in `/api/populate/` inserts a record into `audit_logs` table via `FinalizationStage`.
  - Verify `ApiAuditLogMiddleware` captures custom route requests with `X-Request-ID`.
- [ ] **Task 4.6**: Multi-Dimensional Composite Index Audit:
  - Run `python manage.py check_populate_indexes` across all registered models.
  - Verify that no single-column `INDEX(status)` exists and that `status` is ALWAYS paired with high-cardinality query/report keys (e.g. `reporting_date`, `created_at`, `tenant_id`, `author_id`).
  - Verify B-Tree index prefix hierarchy (equality filters before range filters).

#### Acceptance Criteria for Phase 4:
- [ ] All unit and integration tests run via `python manage.py test core users` pass with 0 errors and 0 regressions.
- [ ] Query compiler produces valid, optimized SQL statements without N+1 bottlenecks.
- [ ] DB locks remain strictly under 10ms.
- [ ] Automated index check passes with 0 missing composite indexes on soft-deleted entities.

---

### Phase 5: Baseline Domain Services & Platform Synergy
*Implement baseline domain services and align dynamic navigation and settings.*

- [ ] **Task 5.1: Domain Services**:
  - [ ] `services/user_service.py`: Password hashing hooks, user lifecycle events.
  - [ ] `services/sidebar_service.py`: Dynamic navigation resolution based on role AccessPolicies.
  - [ ] `services/audit_log_service.py`: Querying and filtering audit records.
- [ ] **Task 5.2: Dynamic Sidebar Navigation**:
  - [ ] Seed initial sidebar navigation items in `sidebars` table.
  - [ ] Verify `POST /api/populate/read/sidebars` returns user-authorized menu trees.
- [ ] **Task 5.3: Standard Response Envelope**:
  - [ ] Ensure all responses strictly adhere to standard `{ "success": true, "data": ..., "count": ... }` shape expected by frontend clients.

#### Acceptance Criteria for Phase 5:
- [ ] `POST /api/populate/read/sidebars` dynamically generates the filtered navigation hierarchy.
- [ ] Service hooks trigger seamlessly during CRUD operations.

---

### Phase 6: Core Deployment Gate & Client Handshake
*Verify that the frontend web and Flutter mobile applications successfully communicate with the new Django backend.*

- [ ] **Task 6.1**: Configure environment variables in Frontend React (`VITE_API_URL`) and Flutter Mobile (`tracker_mobile/lib/api/config.dart`).
- [ ] **Task 6.2**: Test login flow end-to-end from React web application.
- [ ] **Task 6.3**: Test login flow end-to-end from Flutter mobile application.
- [ ] **Task 6.4**: Verify that user profile and dynamic sidebar render accurately on both clients.

#### Acceptance Criteria for Phase 6:
- [ ] Web and Mobile clients authenticate and receive expected session tokens.
- [ ] All standard CRUD tables load data seamlessly through `/api/populate/read/<model>`.

---

## 5. Next Horizon: Planning the AI Daily Work Status System

> [!IMPORTANT]
> **GATEWAY CONDITION**: This section is unlocked ONLY AFTER Phase 1 through Phase 6 are 100% completed and signed off.

Once the Django + MySQL Populate Engine core is live, we will formulate the dedicated technical specification and implementation plan for the **AI-Powered Daily Work Status and Reporting System** (`docs/BRS_AI_Daily_Work_Status_System.docx`).

### Preview of New System Components (To be planned post-core):
1. **Domain Models**:
   - `DailyWorkLog`: Date, author, raw text narrative, submission channel (chat/summary), status.
   - `PersistentTask`: Unique identifier, title, description, owner, status, priority, due date.
   - `TaskActivity`: Date, linked persistent task, log reference, progress milestone, blocker details.
2. **AI Natural-Language Interpretation Engine**:
   - Configurable AI API provider (Gemini / Claude / OpenAI).
   - Strict JSON Schema extraction parser (actions, outcomes, task references, priorities, blockers).
   - Interactive clarification questionnaire engine (disambiguate multi-day tasks without hallucinations).
   - Human-in-the-loop draft review gate (employee reviews and approves before persistence).
3. **Domain Service Lifecycle Hooks**:
   - `services/daily_work_log_service.py`: Transactional commit saving log, task updates, activities, and audit history.
   - `services/persistent_task_service.py`: Automated status and progress event rollups.
4. **Client Interfaces**:
   - Flutter conversational chat input + summary submission screen (`tracker_mobile`).
   - Shared team work feed with real-time filters and activity progress timelines.
   - Managerial performance and blocker analytics dashboard.

---

## 6. Living Progress Tracker & Sign-Off Checklist

| Phase | Description | Status | Completion Date | Sign-Off Notes |
|---|---|---|---|---|
| **Phase 1** | Django & MySQL Scaffold Setup | `PENDING` | - | - |
| **Phase 2** | Core Populate Engine Port | `PENDING` | - | - |
| **Phase 3** | Identity, Auth & User Management (`users`) | `PENDING` | - | - |
| **Phase 4** | Populate Pipeline Integrity Test Suite | `PENDING` | - | - |
| **Phase 5** | Baseline Domain Services & Dynamic Sidebar | `PENDING` | - | - |
| **Phase 6** | Frontend & Flutter Mobile Handshake | `PENDING` | - | - |
| **Phase 7** | Plan & Implement AI Daily Work Status System | `BLOCKED` (Waiting Phase 1-6) | - | Unlocks upon Core completion |

---
*Created by AI Architecture Team for Workhub Tracker (`tracker-v2`).*
