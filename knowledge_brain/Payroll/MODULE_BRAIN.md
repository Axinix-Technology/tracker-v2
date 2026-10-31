# Payroll Module Brain

## Overview
This module governs monthly compensation calculation, versioned salary structures, bulk payroll processing runs, statutory compliance derivations, accounting exports, expense reimbursements, and the Authoritative Monthly Payroll Submission Register.

## Core Architectural Invariants
1. **Zero Manufactured Defaults**: The payroll engine never invents salary structures or statutory rates. Precedence is strictly:
   ```
   SalaryStructure → GeneralSettings.payroll → REJECT
   ```
2. **Configuration Readiness Gate**: In `payroll_run`, any employee lacking a mandatory `SalaryStructure` triggers a `CONFIGURATION_ERROR` note and **blocks final approval** until resolved. Missing employees are never silently omitted.
3. **Accountant Report Projection**: Reports consume frozen `Attendance` snapshots and authoritative `Payroll` documents. Reports never recalculate attendance or payroll independently.
4. **State Machine & Freezing**:
   - `Payroll`: `Draft → Processing → Processed → Approved → Paid` (Financial figures frozen permanently after `Approved`).
   - `PayrollRun`: `Draft → Processing → Computed → Approved → Paid`. Cannot transition to `Approved` if configuration errors exist.

---

## Django Backend Models (`backend_django/payroll/models.py`)

| Model | Target DB Table | Table Type | Aliases | Key Fields | Notes |
|---|---|---|---|---|---|
| `SalaryStructure` | `salary_structures` | `master` | `salary_structures`, `salarystructure` | `employee`, `version`, `effective_from`, `effective_to`, `ctc`, `earnings`, `deductions`, `pf_employee_percent`, `pf_ceiling`, `esi_applicable`, `overtime_rate` | Versioned salary structures with automated closure of prior open windows upon new version creation |
| `PayrollRun` | `payroll_runs` | `transaction` | `payroll_runs`, `payrollrun` | `month`, `year`, `run_status`, `employee_ids`, `payroll_ids`, `total_employees`, `processed_count`, `total_gross`, `total_net`, `audit_events` | Batch monthly payroll processing run with state machine enforcement |
| `Payroll` | `payrolls` | `transaction` | `payrolls` | `employee`, `department`, `month`, `year`, `salary_structure`, `payroll_run`, `working_days`, `present_days`, `lop_days`, `overtime_pay`, `earned_breakdown`, `deduction_breakdown`, `gross_salary`, `net_salary`, `payroll_status` | Authoritative individual monthly payslip ledger with frozen financial breakdowns post-approval |
| `Expense` | `expenses` | `transaction` | `expenses` | `employee`, `client`, `project_type`, `is_billable`, `date`, `expense_period`, `expenses`, `day_total`, `expense_status`, `reimbursed_at` | Employee reimbursement claims with GST tracking, itemized receipt breakdown, and client billable flags |

---

## Django Domain Services (`backend_django/payroll/services.py`)

| Service Class | Target Model | Registered Key | Key Business Logic & Hooks |
|---|---|---|---|
| `SalaryStructureService` | `SalaryStructure` | `salary_structure` | Auto-increments version; automatically closes previous open version; blocks mutation of historical version records; scopes reads to employee |
| `PayrollRunService` | `PayrollRun` | `payroll_run` | Blocks duplicate runs for already Approved/Paid month-years; enforces valid state transitions; restricts execution to Superadmin / Finance HR |
| `PayrollService` | `Payroll` | `payroll` | Row-level employee scoping; blocks modification of frozen financial fields after `Approved`; enforces unique employee-month-year constraint |
| `ExpenseService` | `Expense` | `expense` | Auto-derives `expense_period` (`YYYY-MM`) and sums `day_total`; manages approval/reimbursement state transitions; scopes reads to owning employee |

---

## Legacy Node.js Reference
- Legacy Models: `Backend/src/models/SalaryStructure.js`, `Backend/src/models/PayrollRun.js`, `Backend/src/models/Payroll.js`, `Backend/src/models/Expense.js`.
- Legacy Business Engine: `Backend/src/services/business/payrollEngine.js`, `Backend/src/services/business/payrollSubmissionReport.js`.
