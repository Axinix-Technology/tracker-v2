# Module Brain — Users & Identity Security

## 1. Architectural Overview
- **Models**:
  - `User` (`AbstractUser` registered as `user`, aliases: `employee`, `employees`)
  - `Role` (registered as `role`, aliases: `roles`)
  - Sub-entities: `BasicInfo` (`employee_basic_info`), `ProfessionalInfo` (`employee_professional_info`)
  - Master tables: `Department`, `Designation`, `Company`, `Client`, `ProjectType`
- **Services**:
  - `UserService` in [`users/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/users/services.py)
  - `RoleService` in [`users/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/users/services.py)
  - `MasterDataService` (`DepartmentService`, `DesignationService`, `CompanyService`, `ClientService`, `ProjectTypeService`)

---

## 2. Security & Policy Contracts
- **SuperAdmin Bypass**: Universal check via `context.is_superadmin` grants full management access.
- **Fail-Closed ABAC**:
  - Direct creation, deletion, or modification of `user` and `role` records via generic `/api/populate/` requires administrative privileges (`is_superadmin=True`).
  - Attempted mutations by non-superadmins raise `AuthorizationError` with code `ADMIN_REQUIRED` (HTTP 403).
- **Password PBKDF2 Hashing**:
  - `before_create` and `before_update` execute `make_password(pwd)` before saving.
  - Raw passwords are never written to MySQL.
- **Sensitive Field Guard**:
  - `password` is forbidden from projection in read responses.
  - Non-superadmins cannot modify: `is_superuser`, `is_staff`, `is_superadmin`, `role`, `emp_id`, `status`, `is_deleted`.
