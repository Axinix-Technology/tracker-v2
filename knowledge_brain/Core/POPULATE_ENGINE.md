   # The Populate Engine (Core API Architecture)

   This document centralizes the knowledge regarding the dynamic `populateHelper.js` API, which forms the spine of the entire application. When debugging any API issue, start here.

   ## 1. The Core Files
   The engine is distributed across these crucial core files:

   | Responsibility | File Path |
   |---|---|
   | **Routing & Entry Gates** | `backend/src/routes/populateRoutes.js` |
   | **Dynamic Tenant Model Registry** | `backend/src/models/tenantRegistry.js`, `tenantContext.js` |
   | **Centralized Model Proxy** | `backend/src/models/Collection.js` (`dynamicModelsProxy`) |
   | **Authentication** | `backend/src/Controller/AuthController.js` (`authMiddleware`) |
   | **File Uploads (Multer)**| `backend/src/middlewares/multerConfig.js` (`upload`) |
   | **Request Orchestrator** | `backend/src/helper/populateHelper.js` |
   | **Security & Policies** | `backend/src/utils/policy/policyEngine.js` |
   | **Policy Registry (FBAC)**| `backend/src/utils/policy/registry/` (e.g. `isSelf`, `isManager`) |
   | **CRUD Query Builders** | `backend/src/crud/build*Query.js` |
   | **Data Parsing & Compilation** | `filterParser.js`, `mongoFilterCompiler.js` |
   | **Query Optimization** | `queryOptimizer.js`, `safeAggregator.js`, `defaultPopulateFields.js` |
   | **Data Sanitization** | `sanitizeWrite.js`, `sanitizeUpdate.js`, `sanitizeRead.js`, `sanitizePopulated.js` |
   | **Field Validation** | `validateFieldUpdateRules.js` |
   | **Service Execution** | `servicesCache.js`, `registryExecutor.js` |
   | **Tracing & Auditing** | `requestTracer.js`, `apiHitLogger.js`, `auditLogger.js`, `errorHandler.js` |
   | **Concurrency & Queuing**| `backend/src/services/requestQueue.js` & `raceConditionHandler.js` |
   | **Isolation Verification Gate** | `backend/scripts/verify-zero-static-models.js` |

   ## 2. Multi-Tenant Data-Plane Isolation Invariant

   The Populate Engine enforces **strict multi-tenant database isolation** at the data-plane layer:

   ```text
   JWT Decode / X-Tenant-Id Header
                 ↓
      Tenant Middleware (`tenantMiddleware.js`)
                 ↓
      TenantConnectionManager.getTenantConnection(dbName)
                 ↓
      AsyncLocalStorage Context (`runWithTenantContext`)
                 ↓
      Tenant-Bound User & Session Resolution (`getTenantModel`)
                 ↓
      Module Entitlement Gate (`moduleGateMiddleware.js`)
                 ↓
      Policy Engine & Canonical Model Resolution (`getTenantModel`)
                 ↓
      Generic CRUD Query Builders / Domain Service Hooks
                 ↓
      Isolated Tenant MongoDB Database
   ```

   ### Key Invariants:
   - **Zero Static Model Imports**: Neither CRUD query builders, domain services, crons, nor `authMiddleware` statically import Mongoose model files. All model instances are dynamically resolved from `req.tenantContext.getModel(modelName)` or `getTenantModel(modelName)`.
   - **Canonical Model Map (`CANONICAL_MODEL_NAMES`)**: Normalizes all singular, plural, and case variations (`employee`, `employees`, `Employee`) into a canonical PascalCase name (`Employee`) before database lookup.
   - **Centralized `Collection.js` Proxy (`dynamicModelsProxy`)**: The default export of `Collection.js` is wrapped in a dynamic Proxy that intercepts accesses (`models.employees`, `models.tickets`) and delegates directly to `getTenantModel(prop)`.
   - **Fail-Closed Tenant Resolution**: If tenant identity is missing on non-admin/public endpoints, `tenantMiddleware.js` rejects with **HTTP 400 Bad Request**. If JWT tenantId mismatches `X-Tenant-Id` header, it rejects with **HTTP 403 Forbidden**.

   ## 3. Request Lifecycle (The "One API" Flow)

   When the frontend issues a dynamic request (e.g. `axiosInstance.post('/populate/read/tickets', payload)`), the following sequence occurs:

   1. **Routing & Entry Gates (`tenantMiddleware.js`, `populateRoutes.js`)**: 
      - **Request Tracing (`requestTracer.js`)**: Every incoming request is assigned a unique `req.id` (Trace ID).
      - **Tenant Context Resolution (`tenantMiddleware.js`)**: Resolves tenant connection pool from `TenantConnectionManager`, sets up `AsyncLocalStorage`, and passes context down via `runWithTenantContext()`.
      - **Authentication (`authMiddleware`)**: Validates token and checks session against tenant-bound `Session` model.
      - **Module Entitlement Check (`moduleGateMiddleware.js`)**: Checks if target model's module is enabled in `tenantContext.enabledModules`. Rejects with **HTTP 403 Forbidden** if un-licensed.
   2. **Orchestration & Concurrency (`populateHelper.js`)**: 
      - Checks request action (`read`, `create`, `update`, `delete`, `report`).
      - Enqueues request in **Request Queue** (`requestQueue.js`) for concurrency and rate-limiting.
      - Delegates to `policyEngine.js`.
   3. **Data Parsing & Input Sanitization**:
      - `filterParser.js` tokenizes user filter syntax tree.
      - `mongoFilterCompiler.js` compiles secure NoSQL filter without injection risks.
      - Inputs sanitized via `sanitizeWrite.js` / `sanitizeUpdate.js`.
   4. **Security Check & Policy Routing (`policyEngine.js` & `registry/`)**:
      - Looks up tenant-scoped policy (`${tenantId}:${role}:${modelName}`).
      - Evaluates hybrid RBAC and FBAC (e.g., `isSelf`, `isManager`).
      - Validates field updates using `validateFieldUpdateRules.js`.
   5. **Execution, Hooks, & Query Optimization**:
      - Dynamically resolves model via `ctx.tenantContext.getModel(modelName)`.
      - `registryExecutor.js` executes `before*` lifecycle hooks.
      - CRUD Query Builder executes Mongoose query against the **isolated tenant MongoDB database**.
      - **Fail-Closed Aggregation (`safeAggregator.js`)**: Enforces stage limits ($lookup, $unwind). Fails closed with structured errors if limits are exceeded—**zero fallback `find(10)` queries are executed**.
      - `auditLogger.js` logs mutations.
      - `registryExecutor.js` executes `after*` lifecycle hooks.
   6. **Output Sanitization & Finalization**:
      - Data passed through `sanitizeRead.js` and `sanitizePopulated.js`.
      - Response finalized and logged by `apiHitLogger.js`.

   ## 4. How Business Logic is Injected

   If you need to add custom business logic (e.g., "when a task is created, update the milestone"), **DO NOT edit `populateHelper.js`**. 

   Instead, find or create the corresponding service file in `backend/src/services/` and export the designated lifecycle hooks. Import `models` directly from `Collection.js`:

   ```javascript
   // backend/src/services/tasks.js
   import models from '../models/Collection.js';

   export async function beforeCreate({ data, user }) {
     // Validate or mutate data before saving
     if (!data.dueDate) throw new Error("Due date required");
     return { ...data, status: 'Pending' };
   }

   export async function afterCreate({ doc, user }) {
     // Side-effects execute against tenant-bound models
     const ticket = await models.tickets.findById(doc.ticketId);
     await sendNotification(user, `Task ${doc.title} assigned`);
   }
   ```

   ## 5. Tenant-Scoped Caching Strategy

   To prevent cross-tenant cache contamination:
   - **Navigation Tree Cache (`contextBuilder.js`)**: Scoped by tenant: `${tenantId}:${roleStr}:${userDeptStr}:${userDesigStr}`.
   - **Access Policy Cache (`cache.js`)**: Scoped by tenant: `${tenantId}:${role}`.

   ## 6. Doctor's Diagnostic Cheat Sheet (HTTP Status & Error Matrix)

   When diagnosing an issue in the Populate Engine pipeline, match the HTTP status code and error fingerprint to locate the exact cause:

   | HTTP Status | Error Code / Fingerprint | Root Cause | File to Inspect |
   |---|---|---|---|
   | **400 Bad Request** | `TENANT_IDENTIFIER_MISSING` | Missing JWT `tenantId` or `X-Tenant-Id` header on non-public route | `tenantMiddleware.js` |
   | **400 Bad Request** | `No modelName specified` | Frontend request payload missing target `modelName` parameter | `populateHelper.js` |
   | **401 Unauthorized** | `Access token required` | Missing or expired JWT `Authorization` header | `authMiddleware` |
   | **402 Payment Required**| `TENANT_SUSPENDED` | Tenant account suspended due to billing/policy constraints | `tenantMiddleware.js`, `moduleGateMiddleware.js` |
   | **403 Forbidden** | `TENANT_MISMATCH` | Header `X-Tenant-Id` differs from token's `tenantId` | `tenantMiddleware.js` |
   | **403 Forbidden** | `MODULE_LICENSE_REQUIRED` | Model belongs to a module not enabled in tenant's `enabledModules` | `moduleGateMiddleware.js` |
   | **403 Forbidden** | `⛔ CRITICAL SECURITY: No policy...` | No access policy document defined for `(role, modelName)` | `policyEngine.js`, `cache.js` |
   | **403 Forbidden** | `⛔ ACCESS DENIED: Role... has no...` | Policy exists but explicit `permissions[action]` is `false` | `policyEngine.js`, `Validator.js` |
   | **500 Internal Error** | `[safeAggregate] Threshold exceeded` | Aggregation pipeline breached `$lookup` (9) or `$unwind` (9) stage limits | `safeAggregator.js` |
   | **500 Internal Error** | `[ServiceHookError]` | Unhandled exception thrown inside domain service `before*` / `after*` hook | `backend/src/services/<model>.js` |

   ## 7. Populate Strategy: Flat Populate & Path Collision Guard

   > **Critical**: `buildReadQuery.js` uses a **flat populate** approach. Each dot-notation path from `defaultPopulateFields.js` is checked directly against the Mongoose schema and populated individually.

   ### How Flat Populate Works
   ```text
   populateFields = {
     "professionalInfo.designation": "title",
     "professionalInfo.department": "name"
   }

   → Schema check: schema.path("professionalInfo.designation") → ObjectId ref ✓
   → Schema check: schema.path("professionalInfo.department") → ObjectId ref ✓
   → query.populate([
        { path: "professionalInfo.designation", select: "title" },
        { path: "professionalInfo.department", select: "name" }
     ])
   ```

   ### Path Collision Guard (`sanitizeRead.js`)
   `sanitizeRead.js` automatically collapses parent/child field conflicts before executing queries:
   - **Input**: `['professionalInfo', 'professionalInfo.designation']`
   - **Output**: `['professionalInfo']` (child path removed, top-level parent covers nested fields)
   This prevents Mongoose `.select()` projection collision errors globally across main queries and populated sub-queries.

   ## 8. Preventive Maintenance Checklist for Developers

   Before committing code touching the Populate Engine:
   1. **Run Static Model CI Check**: `node backend/scripts/verify-zero-static-models.js` (Must pass with 0 static imports).
   2. **No Direct Model Imports**: Services must consume models exclusively via `import models from '../models/Collection.js'` or `req.tenantContext.getModel()`.
   3. **No Logic in Controllers**: Controllers must remain generic orchestrators; all domain rules must live in `backend/src/services/<model>.js` hooks.
   4. **Tenant Cache Invalidation**: When modifying sidebar navigation or access policies, trigger `clearNavigationCache()` or `invalidatePermissions()`.

   ## 9. Developer Freedom & Anti-Frustration Policy: How to Handle Complex Requirements Without Custom Routes

   Developers must never feel that the Populate Engine is restrictive or that they must build a custom Express/Django route to get their work done. All complex business logic is 100% supported via Populate:

   1. **Custom Business Actions & State Transitions ("Approve", "Reject", "Cancel", "Publish")**:
      - Instead of `POST /api/leave/123/approve`, call `/api/populate/update/leave/123` with payload `{"action_intent": "approve", "remarks": "..."}`.
      - Handled cleanly in `services/leave.js` (or Django `LeaveService`) inside `beforeUpdate` / `afterUpdate`.
   2. **Bulk / Batch Operations ("Close 50 Tickets", "Bulk Assign")**:
      - Instead of `POST /api/tickets/bulk-close`, call `/api/populate/bulk_update/ticket` with `{"ids": [...], "data": {"status": "CLOSED"}}`.
      - Runs atomically in a single transaction with service hooks and audit logging per row.
   3. **Aggregations & Analytics (Dashboard Metrics, Group By, Totals)**:
      - Instead of `GET /api/reports/dashboard`, call `/api/populate/aggregate/<model>` passing `filter`, `groupBy`, and `metrics` (`$count`, `$sum`, `$avg`).
      - Compiles to optimized SQL `GROUP BY` with automatic ABAC and tenant isolation.
   4. **File & Image Uploads (Multipart Form-Data)**:
      - Instead of `POST /api/employees/avatar`, call `/api/populate/create/<model>` or `/update/<model>/<id>` using `multipart/form-data` with `data` (JSON string) and file attachments.
      - Automatically uploads to S3/R2/local, replaces keys with file URLs, and passes to service hooks.
   5. **Dry-Run / Preview Calculations (Taxes, Overtime, Leave Balance)**:
      - Instead of `POST /api/payroll/calculate`, call `/api/populate/create/payroll?dry_run=true`.
      - Computes all formulas in `beforeCreate`, returns calculated results in the response, and rolls back the DB transaction.
   6. **Multi-Model Sagas (Parent + Child Nested Creates)**:
      - Instead of `POST /api/orders/checkout`, send nested JSON to `/api/populate/create/order`.
      - Parent is created by the pipeline; child entities (`OrderItem`) are created inside `afterCreate` within the same transaction.
   7. **Export to Excel / CSV**:
      - Instead of `GET /api/tickets/export-excel`, call `/api/populate/export/<model>?format=xlsx|csv` with the exact same AST filter as the table view.

   ### The 3-Point Strict Exemption Policy (When a Custom Route IS Legitimate)
   A custom router/controller is ONLY permitted if it meets at least one of these 3 physical criteria:
   1. **Raw Cryptographic Signature Verification**: Webhooks requiring verification of raw, unparsed HTTP request body bytes before JSON parsing (e.g., Stripe, Razorpay HMAC, GitHub webhooks).
   2. **Stateful Session Handshakes**: Interactive auth handshakes (OAuth2 redirects, SAML/SSO callbacks, WebAuthn/FIDO2).
   3. **Continuous Binary Streaming**: Non-JSON streaming where buffering into memory or S3 is impossible (live video transcoding, 5GB dynamic ZIP archive stream).
   *If it does not meet one of these 3, it CAN and MUST be handled in Populate + Service Hooks.*

   ## 10. Granular Pipeline Directives & Per-Model Limit Overrides (Safe Defaults, Flexible Tuning)

   To prevent developers from feeling that global limits (e.g. 5s query timeout, 3 prefetch depth, read auditing) are a bottleneck:
   - **Non-Negotiable (Never Bypassed)**: Parameterized SQL compilation, tenant data-plane isolation, ABAC authorization, and dangerous input sanitization.
   - **Configurable / Tunable Per Model**:
     1. **Selective Read Auditing**: Mutations (`create`, `update`, `delete`) are always audited. High-frequency models (`GeneralSettings`, `Notification`) skip read auditing to avoid 10M row database bloat; sensitive models (`Payroll`) opt-in to `audit_reads=True`.
     2. **Model Resource Overrides**: Heavy reporting models can declare higher limits: `@register_model('report', max_prefetch_depth=5, query_timeout_ms=15000, max_page_limit=500)`.
     3. **Query Caching (`cache_ttl=300`)**: Master lookups (`Country`, `Department`) serve reads directly from Redis/memory in <2ms, bypassing MySQL entirely.
     4. **Safe Aggregations (`allow_aggregations=True`)**: Unlocks SQL `GROUP BY` and metrics exclusively for models with verified composite indexes.

   ## 11. Canonical 10-Stage Pipeline Sequence (Fail-Fast & Anti-Crash Architecture)

   The pipeline enforces strict fail-fast ordering to protect CPU and memory:

   | Stage | Name | Key Function & Fail-Fast CPU Rationale | Fail Code |
   |---|---|---|---|
   | **01** | `PreFlightStage` | Content-Length inspection (`<= 10MB`), $O(1)$ password length check (`<= 128 chars`), Request ID injection. Kills DoS in `<0.01ms` before parsing or hashing. | `HTTP 400` / `413` |
   | **02** | `IngressParseStage` | Safe JSON parsing (depth $\le 10$), multipart boundary check (no S3 upload yet), canonical action/model resolution. | `HTTP 422` |
   | **03** | `AuthContextStage` | **Strict Tenant Binding**: Authenticated tokens bind tenant **strictly from the token `tid` claim** (headers cannot override). Anonymous requests resolve via subdomain/header. Bearer JWT/Session auth. Binds cached `GeneralSettings`. | `HTTP 400` / `401` |
   | **04** | `RateLimitStage` | Evaluates Redis rate limits per User / IP / Tenant: Anon (60/min), User (600/min), Telemetry (600/min). Idempotency pre-check. Fails in `<0.1ms`. | `HTTP 429` |
   | **05** | `AuthorizationStage` | Module entitlement check (`enabled_modules`), `PUBLIC_READ_MODELS` / `PUBLIC_CREATE_MODELS` check, ABAC policy evaluation, `IMMUTABLE_MODELS` / `GLOBAL_MODELS` write blocks. **Fails fast before any upload or DB connection!** | `HTTP 401` / `403` / `405` |
   | **06** | `ValidationStage` | Pydantic schema validation, field policy projection (strips forbidden fields from payload, filters, order, and `groupBy`/`metrics`). **Post-Auth File Upload**: Streams to S3 only after auth passes! | `HTTP 400` / `422` |
   | **07** | `CompilationStage` | AST parsing, joins up to max depth ($\le 3$), parameterized SQL compilation. Session timeout enforced: `SET SESSION max_execution_time=5000; innodb_lock_wait_timeout=5`. | `HTTP 400` / `422` |
   | **08** | `ExecutionStage` | Cache check (`cache_ttl`), **Service `before_*` Hooks (Fail-Closed: aborts transaction on error)**, atomic DB transaction, **Service `after_*` Hooks (Fail-Safe: runs on `transaction.on_commit`)**. | `HTTP 400` / `500` / `504` |
   | **09** | `SerializationStage` | OOM-safe streaming (`QuerySet.iterator(chunk_size=1000)`), CSV formula injection prefix (`=+-@` prefixed with `'`), signed download links, Tamil Unicode (`ensure_ascii=False`). | `HTTP 500` |
   | **10** | `FinalizationStage` | Caches idempotency envelope in Redis, returns JSON response to client immediately (**`<5ms`**), dispatches non-blocking sanitized audit log to async worker pool. | Delivered |

   ## 12. Python Django Implementation (`backend_django`) & Git-Pip Architecture

   The Python implementation runs in parallel with the Node.js backend:
   - **Kernel Distribution**: `django-populate-core` is installed cleanly via pip from GitHub (`pip install git+ssh://git@github.com/Axinix-Technology/Axinix-Core.git`). Zero local folder dependencies or `POPULATE_CORE_PATH` environment overrides.
   - **Modular Product Apps**: Directly reflecting the commercial packaging defined in `tenantRegistry.js`:
     - `users/` (Core: `Role`, `Department`, `Designation`, `Company`, `Client`, `ProjectType`, `User`)
     - `tasks/` (Product: `Task`, `TaskType`, `Sprint`, `Todo`, `TaskService`)
     - `tickets/` (Product: `Ticket`, `TicketComment`, `TicketAttachment`, `TicketService`)
     - `attendance/` (Product: `Attendance`, `Shift`, `AttendancePolicy`, `Holiday`, `AttendanceService`)
   - **Dual Routing Compatibility**: Routes both `/api/populate/` and `/populate/` directly into `populate_core.urls`, allowing zero frontend API code changes.


