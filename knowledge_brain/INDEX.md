# Living Knowledge Brain — Master Index

> **Strict Alphabetical Indexing of System Architecture, Modules, Services, and Rules**
> Adheres strictly to Rule 2 (Living Knowledge Brain with Alphabetical Indexing).

---

## Master Directory Index

- [Assets](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Assets/MODULE_BRAIN.md) — Asset Management suite: models, procurement, assignments, stock ledger, deprecations.
- [Attendance](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Attendance/MODULE_BRAIN.md) — Attendance suite: punch regularization, leaves, comp-off, and holiday calendars.
- [Billing](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Billing/MODULE_BRAIN.md) — Client Invoicing & Accounting suite: quotations, revisions, order acknowledgements, invoices, payments, journals, ledgers, period closures.
- [Common](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Common/) — Shared utilities, system constants, and base exceptions.
- [ControlPlane](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/ControlPlane/MODULE_BRAIN.md) — Multi-Tenant Control Plane: organization directories, user logins, and database provisioning logs.
- [Core](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Core/) — Django Populate Core pipeline (10-stage execution engine, ABAC, and audit logger).
- [CRM](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/CRM/MODULE_BRAIN.md) — Customer Relationship Management: leads, contacts, opportunities, deal pipelines, and client meetings.
- [Dashboard](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Dashboard/) — Dynamic role-based dashboard layouts, widget schemas, and KPI aggregation.
- [Feed](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Feed/MODULE_BRAIN.md) — Feed & Team Collaboration suite: groups, channels, posts, comments, and direct messaging.
- [HR](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/HR/MODULE_BRAIN.md) — Human Resources suite: employee documents, career progression lifecycles, corporate policies, and user overrides.
- [Notifications](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Notifications/MODULE_BRAIN.md) — Real-time event notifications, strict recipient isolation, and anti-spoofing sender guards.
- [Payroll](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Payroll/MODULE_BRAIN.md) — Compensation & Payroll suite: salary structures, batch payroll runs, payslips, and reimbursement expenses.
- [Profile](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Profile/MODULE_BRAIN.md) — User profiles, BasicInfo and ProfessionalInfo synchronization.
- [Recruitment](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Recruitment/MODULE_BRAIN.md) — Recruitment & Onboarding: job openings, candidate pipeline, and onboarding checklists.
- [System](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/System/MODULE_BRAIN.md) — System Telemetry: status configurations, mappings, email SMTP configs, release notes, and workflows.
- [Tasks](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Tasks/MODULE_BRAIN.md) — Agile Task Management: boards, sprints, time tracking sessions, queues, daily activities, and stage histories.
- [Tickets](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Tickets/MODULE_BRAIN.md) — Client Support & Ticketing: SLA resolution, activity logs, participants, and status transitions.
- [Users](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/Users/MODULE_BRAIN.md) — Identity, RBAC security, password PBKDF2 hashing, and privilege escalation guards.
- [_SYSTEM](file:///d:/Axinix%20Projects/tracker-v2/knowledge_brain/_SYSTEM/) — Cross-module database relationships and shared master configurations.

---

## Phase 1 Implementation Summary: Security Core & Credential Guard

### 1. `users` Module Fortification
- **Domain Service Layer**: Implemented [`users/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/users/services.py) registering `UserService`, `RoleService`, `DepartmentService`, `DesignationService`, `CompanyService`, `ClientService`, `ProjectTypeService`.
- **Password PBKDF2 Hashing**: Auto-hashes passwords via `django.contrib.auth.hashers.make_password` inside `before_create` and `before_update`. Plaintext passwords are never persisted to MySQL.
- **Privilege Escalation Prevention**: Creation, deletion, and privilege alterations (`is_superuser`, `is_staff`, `role`, `status`) strictly require `context.is_superadmin`. Non-superadmins attempting mutations receive HTTP 403 `ADMIN_REQUIRED`.
- **Projection Sanitization**: `password` is globally registered in `get_forbidden_fields` ensuring password hashes are never exposed in read queries.

### 2. `notifications` Module Fortification
- **Strict Recipient Row Scoping**: Enforces `before_read` and `get_policy_scope` returning `Q(recipient=context.user)`. Employees are strictly restricted to their own notifications, preventing organization-wide data leakage.
- **Anti-Spoofing Sender Binding**: `before_create` overrides any client-supplied `sender` field with `context.user.id`.
- **Ownership Verification on Updates**: `before_update` guarantees users can only modify/read-mark notifications where `instance.recipient == context.user`. Scoped queryset returns 404 for notifications belonging to other users.

---

## Phase 2 Implementation Summary: HR, Short Permissions & Timesheet Substrate (Phase 1 Migration)

### 1. `hr` Dedicated App Creation (`backend_django/hr/`)
- **Domain Service Layer**: Implemented [`hr/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/hr/services.py) with `EmployeeDocumentService`, `EmployeeLifecycleHistoryService`, `HRPolicyService`, and `UserOverrideService`.
- **`EmployeeDocument`**: Personal document compliance and verification (Aadhaar, PAN, Passport, Degree, Experience, Relieving) with `Pending` -> `Approved`/`Rejected` approval status.
- **`EmployeeLifecycleHistory`**: Immutable progression ledger recording career changes (`Promotion`, `Transfer`, `SalaryRevision`, `DesignationChange`, `DepartmentChange`, `ManagerChange`).
- **`HRPolicy`**: Centralized corporate governance policies with role and department scoping, acknowledgment tracking, and versioning.
- **`UserOverride`**: Granular per-user UI visibility capability overrides (`allow`/`deny`) for frontends.

### 2. `attendance` Additions (`backend_django/attendance/`)
- **`HolidayOverride`**: Branch/Department specific working-day and holiday adjustments with compensation policies (`COMP_OFF`, `DOUBLE_PAY`, `OVERTIME_MULTIPLIER`).
- **`PermissionBalance`**: Monthly short-duration permissions quota (e.g. 2 hours/month) with unique constraints per employee, year, and month.
- **`PermissionTransaction`**: Permission request and auto-consumption tracking (`LATE_CHECKIN`, `EARLY_CHECKOUT`, `PERSONAL_OUTING`).

### 3. `tasks` Daily Activity Timesheet Substrate (`backend_django/tasks/`)
- **`DailyActivity`**: Daily activity and work logging linked to clients, project types, task types, and assignees, establishing the foundation for the AI Daily Work Status and Reporting System.

---

## Phase 3 Implementation Summary: Compensation & Payroll Suite (Phase 2 Migration)

### 1. `payroll` Dedicated App Creation (`backend_django/payroll/`)
- **Domain Service Layer**: Implemented [`payroll/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/payroll/services.py) registering `SalaryStructureService`, `PayrollRunService`, `PayrollService`, and `ExpenseService`.
- **`SalaryStructure`**: Multi-component compensation versioning with automated closure of preceding open effective date windows.
- **`PayrollRun`**: Batch monthly computation runs with state machine enforcement (`Draft` &rarr; `Processing` &rarr; `Computed` &rarr; `Approved` &rarr; `Paid`). Subsequent runs for completed months are blocked.
- **`Payroll`**: Immutable monthly payslip ledger. Freezes financial breakdown figures permanently upon `Approved` status.
- **`Expense`**: Employee reimbursement claims with GST tracking, itemized receipt breakdown, client billable flags, and approval/reimbursement lifecycles.


---

## Phase 4 Implementation Summary: Architecture Parity & Service Layer Hardening

### 1. Dynamic Policy Evaluation Alignment
- **Preemption Trap Elimination**: Resolved across `SalaryStructureService`, `PayrollService`, `EmployeeDocumentService`, `ExpenseService`, and `DailyActivityService`. `check_permission` defers with `None` so that `PolicyEngine` Stage 5 systematically evaluates database `AccessPolicy` records and dynamic ABAC conditions (`is_owner`, `matches`).
- **Multi-Tenant Scope Decoupling**: Updated `get_policy_scope` in `hr/services.py`, `payroll/services.py`, `attendance/services.py`, and `tasks/services.py` to check `PolicyEngine.has_capability(...)`. Users with managerial or administrative capabilities (`.read`, `.all`) can query company-wide records, while standard employees gracefully default to self-ownership scopes.
- **Universal SuperAdmin Resolution**: Replaced brittle `getattr(context.user, "is_superadmin", False)` with canonical `context.is_superadmin` property, recognizing flags on `context.user`, `context.user.role.is_superadmin`, and `context.user.is_superuser`.
- **HR Policy Mutation Sanitization**: Fixed security defacement gap in `HRPolicyService.before_update`. Non-manager employee self-acknowledgments strictly purge all incoming keys and only update the `acknowledgments` list.
- **Transaction Cleanliness**: Eliminated redundant nested `transaction.atomic()` blocks inside `after_create` across attendance and task services.


---

## Phase 5 Implementation Summary: Client Invoicing & Accounting Suite (Phase 3 Migration)

### 1. `billing` Dedicated App Creation (`backend_django/billing/`)
- **Domain Service Layer**: Implemented [`billing/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/billing/services.py) registering `QuotationService`, `QuotationRevisionService`, `OrderAcknowledgementService`, `InvoiceService`, `PaymentService`, `PaymentJournalService`, `ClientLedgerService`, and `PeriodClosureService`.
- **`Quotation` & `QuotationRevision`**: Client quotation workflow with auto-generated sequential numbers (`QUO-YYYY-XXXX`), line item discount/tax computation, and immutable state snapshots (`billing_quotation_revisions`) upon revision requests.
- **`OrderAcknowledgement`**: Formal customer contract commitments (`OA-YYYY-XXXX`) tracking agreed module scopes, sales owners, and internal/client approvals.
- **`Invoice`**: Accounts receivable billing (`INV-YYYY-XXXX`) with automatic status synchronization (`Draft` &rarr; `Issued` &rarr; `Partially Paid` &rarr; `Paid`), balance due calculation, and frozen financial figures on paid/cancelled invoices.
- **`Payment` & `PaymentJournal`**: Customer collections reconciliation updating invoice balances and bank receipt verification journals (`RCT-YYYY-XXXX`).
- **`ClientLedger`**: Double-entry financial audit trail with immutable debit (invoices) and credit (payments) entries and running balance derivation.
- **`PeriodClosure`**: Multi-module accounting period locks (`billing_period_closures`) with overlap prevention.

### 2. `assets` Additions (`backend_django/assets/`)
- **`AssetInvoice`**: Vendor equipment purchase invoices linked to `AssetPurchase` records with payment milestone tracking.
- **`AssetPayment`**: Vendor hardware purchase payments with automatic invoice status completion upon total settlement.


---

## Phase 6 Implementation Summary: CRM & Recruitment Suites (Phase 4 Migration)

### 1. `crm` Dedicated App Creation (`backend_django/crm/`)
- **Domain Service Layer**: Implemented [`crm/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/crm/services.py) registering `LeadTypeService`, `ReferenceTypeService`, `ContactService`, `OpportunityService`, `CRMActivityService`, and `CRMMeetingService`.
- **`Contact`**: Prospect pipeline with contact interaction history (`contact_history`), sales ownership, and automatic client generation (`users_clients`) upon status conversion to `Converted`.
- **`Opportunity`**: Sales deal management with deterministic probability mapping (`New`: 10% &rarr; `Discovery`: 20% &rarr; `Proposal`: 50% &rarr; `Negotiation`: 80% &rarr; `Won`: 100% / `Lost`: 0%), mandatory loss reason checks, and cross-module linkages to quotations and contracts.
- **`CRMActivity` & `CRMMeeting`**: Chronological customer touchpoint logging and calendar scheduling with conflict and duration guards (`scheduled_time < end_time`).

### 2. `recruitment` Dedicated App Creation (`backend_django/recruitment/`)
- **Domain Service Layer**: Implemented [`recruitment/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/recruitment/services.py) registering `JobCategoryService`, `JobTypeService`, `JobOpeningService`, `CandidateService`, `OnboardingTemplateService`, and `OnboardingService`.
- **`JobCategory` & `JobType`**: Classification masters for time tracking, hourly billing rates, productivity benchmarks, and stage derivation rules.
- **`JobOpening`**: Public career board and vacancy listings with opening/filled quota tracking and automatic publication timestamps.
- **`Candidate`**: Applicant tracking with auto-generated sequential identifiers (`APP-YYYY-XXXX`), interview rating scores, offer letters, and automatic quota updates upon `Hired` stage.
- **`Onboarding` & `OnboardingTemplate`**: Configurable employee onboarding blueprints with automated checklist instantiation, real-time completion/verification percentage derivation, and SLA breach tracking.


---

## Phase 7 Implementation Summary: System Telemetry & Control Plane Suites (Phase 5 Migration)

### 1. `system` Dedicated App Creation (`backend_django/system/`)
- **Domain Service Layer**: Implemented [`system/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/system/services.py) registering `StatusConfigService`, `StatusMappingService`, `EmailConfigService`, `ServiceProviderService`, `ReleaseNoteService`, `ResourceService`, `WorkflowService`, and `ProductService`.
- **`StatusConfig` & `StatusMapping`**: Dynamic status metadata catalog and cross-model state synchronization pairing linked entities (e.g. tasks and tickets).
- **`EmailConfig`**: Outbound SMTP credential management enforcing mandatory password redaction in API responses (`get_forbidden_fields`).
- **`ServiceProvider`**: External contractor and service provider master directory with GSTIN/PAN and banking metadata.
- **`ReleaseNote`**: Version release notes and categorized changelogs with per-user read tracking (`seen_by`).
- **`Resource`**: Canonical business resource registry decoupling frontend `can()` permissions from model names.
- **`Workflow`**: Declarative multi-step approval, escalation, and onboarding workflow graphs.
- **`Product`**: Commercial product catalog for quotation and invoice line items.

### 2. `control_plane` Dedicated App Creation (`backend_django/control_plane/`)
- **Domain Service Layer**: Implemented [`control_plane/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/control_plane/services.py) registering `TenantService`, `UserLoginService`, `ModuleService`, and `ProvisioningRunService`.
- **`Tenant`**: Multi-tenant organization directory with subdomain routing, tenant ID, isolated database name derivation (`tracker_<subdomain>`), and plan tiers.
- **`UserLogin`**: Central authentication routing directory linking global emails to specific tenants and tenant database primary keys.
- **`Module`**: System feature entitlement catalog declaring allowed collections/models per module.
- **`ProvisioningRun`**: Multi-tenant database provisioning and schema migration audit ledger.

---

## Phase 8 Implementation Summary: Frontend Routing Integrity & Pure Populate Contract Verification

### 1. Sacred Law 8 Compliance (`Frontend/src/pages/`)
- **Pure Page-Only Routing**: Eradicated all non-page modals, sub-components, and configuration files from `Frontend/src/pages/` to prevent Vite Plugin Pages phantom routes:
  - Relocated `ShiftEditorModal.jsx`, `AttendancePolicyEditor.jsx`, and `AttendancePreviewModal.jsx` to `Frontend/src/components/Attendance/`.
  - Relocated `Academy` sub-components (`AcademyHero.jsx`, `RequestJourney.jsx`, `SecurityLayer.jsx`, `CrudEngine.jsx`, `FeatureBuilder.jsx`, `DebuggingJourney.jsx`, `CodeBlock.jsx`, `ReferencePanel.jsx`) to `Frontend/src/components/Academy/`.
  - Relocated `Task.jsx` legacy card to `Frontend/src/components/Tasks/TaskLegacyCard.jsx`.
  - Relocated `Frontend/src/pages/attendance/dailyTracker/activity.jsx` to `Frontend/src/components/Attendance/DailyActivityView.jsx`.
  - Relocated `Frontend/src/pages/crm/quotations/config.js` to `Frontend/src/constants/quotationsConfig.js`.
  - Fixed props destructuring on `Frontend/src/pages/attendance/leave-regularization.jsx` with default `{}` fallback.
- **Audit Verification**: Scanned all 153 route files in `Frontend/src/pages/`: 100% have valid default exports with 0 non-defaulted props.

### 2. Populate API & Model Aliases Parity
- **Populate Gateway Alignment**: Frontend `PopulateApi` methods (`/populate/read/:model`, `/populate/create/:model`, `/populate/update/:model/:id`, `/populate/delete/:model/:id`, `/populate/report/:model`) dispatch through `axiosInstance` directly into Django `PopulateAPIView`.
- **Auth Endpoint Parity**: `/auth/login`, `/auth/logout`, `/auth/me`, `/auth/me/context`, and `/auth/change-password` map 1:1 with `backend_django/users/urls.py`.
- **Registered Model Aliases**:
  - `tasks` &rarr; `Task`
  - `tickets` &rarr; `Ticket`
  - `employees` &rarr; `Employee`
  - `clients` &rarr; `Client`
  - `project_types` &rarr; `ProjectType`
  - `payroll_runs` &rarr; `PayrollRun`
  - `payslips` &rarr; `Payroll`
  - `salary_structures` &rarr; `SalaryStructure`
  - `employee_life_cycle_histories` &rarr; `EmployeeLifecycleHistory`
  - `shifts` &rarr; `Shift`
  - `departments` &rarr; `Department`
  - `dashboard_schemas` &rarr; `DashboardSchema`
  - `dashboard_widgets` &rarr; `DashboardWidget`
- **Build Verification**: Vite production build transforms all 5,412 modules into production bundles in 22.88s with exit code 0.

---

## Phase 9 Implementation Summary: SEO Engine, Performance Optimization & Production Hardening

### 1. Build Optimization & Vendor Chunk Splitting (`Frontend/vite.config.js`)
- **Source Map Hardening**: Disabled production source maps (`build.sourcemap: false`) to prevent source code reverse engineering and eliminate `.map` asset payloads.
- **Rollup Manual Chunk Architecture**:
  - `vendor-react`: `react`, `react-dom`, `scheduler` (248 kB, gzip: 79 kB).
  - `vendor-router`: `react-router`, `react-router-dom` (37 kB, gzip: 13 kB).
  - `vendor-icons`: `lucide-react` (580 kB, gzip: 154 kB).
  - `vendor-network`: `axios`, `js-cookie`, `jwt-decode` (53 kB, gzip: 20 kB).
  - `vendor-geo-countries`: `country-state-city/lib/country` (96 kB, gzip: 14 kB).
  - `vendor-geo-states`: `country-state-city/lib/state` (555 kB, gzip: 121 kB).
  - `vendor-excel`: `xlsx`, `file-saver` (426 kB, gzip: 142 kB).
  - `vendor-editor`: `react-quill-new` (208 kB, gzip: 62 kB).
  - `vendor-ui`: `clsx`, `tailwind-merge`, `react-hot-toast` (isolated lightweight UI helpers).
- **Zero Oversized Chunks**: Eradicated the uncompressed 8.7MB `city.json` bundle by standardizing city inputs as clean text fields across all schemas (`ClientForm`, `employeeForm`, `vendors`, `profileForm`), switching to modular subpath imports (`country-state-city/lib/country.js` and `country-state-city/lib/state.js`), and splitting geo chunks into `vendor-geo-countries` and `vendor-geo-states`. Every single chunk is strictly under 600 kB with zero Vite warnings.

### 2. Centralized Console Logging & Environment Protection (`Frontend/src/utils/logger.js`)
- **Production Console Silencing**: Suppresses `console.log`, `console.debug`, and `console.info` in production builds (`import.meta.env.PROD`).
- **Telemetry & Error Sanitization**: Sanitizes `console.error` and `console.warn` outputs to prevent auth tokens (Bearer JWTs) and raw stack traces from leaking to end users.
- **Bootstrap Initialization**: Activated in `Frontend/src/main.jsx`.

### 3. Dynamic SEO Head & OpenGraph Engine (`Frontend/src/components/SeoHead.jsx`)
- **Dynamic Title & Canonical Injection**: Automatically derives route title from `location.pathname` and dynamically updates `<title>` and `<link rel="canonical">`.
- **Zero Framework Leakage**: Browser tabs never leak default names like "Vite App" or "React App".
- **Social Tags**: Injects OpenGraph (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`) and Twitter Cards.

### 4. Semantic Crawlable Pre-Render Shell (`Frontend/index.html`)
- **SPA Zero-Visibility Resolution**: Injected pre-hydration semantic HTML structure (`<header>`, `<nav>`, `<main>`, `<section>`, `<h1>`, `<h2>`, `<article>`, `<footer>`) inside `<div id="root">`.
- **Bot Discoverability**: Raw HTTP scrapers and AI search crawlers (`Googlebot`, `Bingbot`, `GPTBot`, `ClaudeBot`, `PerplexityBot`) immediately receive rich semantic body content without executing JavaScript. React seamlessly hydrates over the shell on client bootstrap.
- **Accessible `<noscript>` Fallback**: Guarantees user agent accessibility.
- **Schema.org Structured Data**: Integrated `WebApplication` JSON-LD specification.

### 5. Static Discovery Assets & Directives (`Frontend/public/`)
- **`robots.txt`**: Explicit directives for search crawlers, dedicated allowances for AI bots (`GPTBot`, `ClaudeBot`, `PerplexityBot`, etc.), protected private ERP paths (`/settings/`, `/payroll/`, `/api/`), and explicit allowances for public discovery endpoints.
- **`llms.txt`**: LLM context specification detailing WorkHub modules, Populate API pipeline, and platform documentation routes.
- **`sitemap.xml`**: Compliant XML sitemap indexing all canonical public platform routes.

### 6. Branded 404 Recovery Page (`Frontend/src/pages/[...all].jsx`)
- **Catch-All Routing**: Registered under `vite-plugin-pages` to catch all unmapped routes.
- **Design Tokens & Recovery**: Uses WorkHub ERP design tokens (`--brand-solid`, `--surface-1`) providing clear navigation back to the Dashboard (`/dashboard`) or previous screen.
