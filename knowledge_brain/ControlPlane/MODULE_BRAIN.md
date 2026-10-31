# Module Brain: Multi-Tenant Control Plane

> **Domain:** Multi-Tenant Organization Directory, Global Routing, Module Entitlements, and Provisioning Logs.  
> **App Location:** `backend_django/control_plane/`  
> **Tables:** `control_plane_tenants`, `control_plane_user_logins`, `control_plane_modules`, `control_plane_provisioning_runs`.

---

## 1. Domain Overview & Principles

The Control Plane manages platform-wide multi-tenancy, cross-tenant identity routing, and organization provisioning:
1. **Tenant (`Tenant`)**: Organization master records containing subdomain routing, tenant ID, isolated MySQL database names, active plan, and enabled modules (`enabled_modules`).
2. **User Login (`UserLogin`)**: Central authentication routing directory linking a user's global email address to their specific tenant organization and tenant database primary key (`user_id`).
3. **Module (`Module`)**: Global catalog of product modules (e.g. `hrms`, `attendance`, `payroll`, `billing`, `crm`, `recruitment`) declaring allowed collection/table keys.
4. **Provisioning Run (`ProvisioningRun`)**: Immutable audit log of database provisioning, migration executions, and tenant initialization runs.

---

## 2. Backend Models

| Model | Table | Key Fields |
|---|---|---|
| `Tenant` | `control_plane_tenants` | `tenant_id`, `name`, `subdomain`, `database_name`, `plan`, `status`, `enabled_modules`, `settings` |
| `UserLogin` | `control_plane_user_logins` | `email`, `tenant`, `user_id`, `is_superadmin`, `is_active`, `last_login` |
| `Module` | `control_plane_modules` | `module_id`, `name`, `description`, `collections`, `is_active` |
| `ProvisioningRun` | `control_plane_provisioning_runs` | `tenant`, `database_name`, `status`, `steps_completed`, `error_message`, `initiated_by`, `started_at` |

---

## 3. Services & Hook Lifecycles

### TenantService (`@register_service("tenant")`)
- **Subdomain Normalization**: Lowercases and sanitizes incoming subdomain strings (`my-company`).
- **Database Derivation**: Automatically sets `database_name = tracker_<subdomain>` if not explicitly provided.
- **Access Guard**: Organization modification requires superadmin privileges, while subdomain availability checks are publicly readable.

### UserLoginService (`@register_service("user_login")`)
- Guarantees `(email, tenant)` uniqueness and maintains cross-tenant routing pointers.

