# Attendance Module Brain

## Overview
This module governs daily attendance tracking, shift scheduling, punctuality rules, overtime derivation, leave transactions, regularizations, and immutable policy snapshotting.

## Core Architectural Invariant
**Strict Policy-Driven Execution**: Zero hardcoded business thresholds (hours, grace periods, OT caps, LOP multipliers) exist in business handlers. If no valid policy or shift is resolved for an employee on a target date, the engine fails explicitly with `ATTENDANCE_POLICY_REQUIRED` rather than manufacturing fallback values.

### Resolution Precedence
```
AttendancePolicy → Shift → GeneralSettings → REJECT
```

## Backend Models
| Model | Node.js File | Django Model (`backend_django/attendance/models.py`) | MySQL Table | Key Fields | Notes |
|---|---|---|---|---|---|
| `Attendance` | `Attendance.js` | `Attendance` | `attendances` | `employee`, `date`, `check_in`, `check_out`, `work_hours`, `overtime_hours`, `status` | Daily tracking; synced automatically on approved leaves/WFH. |
| `AttendancePolicy` | `AttendancePolicy.js` | `AttendancePolicy` | `attendance_policies` | `name`, `grace_period_mins`, `half_day_threshold_hours`, `full_day_threshold_hours` | Threshold rules. |
| `Shift` | `Shift.js` | `Shift` | `shifts` | `name`, `start_time`, `end_time`, `grace_period_mins`, `is_active` | Work windows and scheduled hours. |
| `ShiftAssignment` | `Shift.js` | `ShiftAssignment` | `shift_assignments` | `employeeId`, `shiftId`, `start_date`, `end_date`, `is_active` | Date-ranged employee shift allocation. |
| `LeaveType` | `LeaveTypes.js` | `LeaveType` | `leave_types` | `name`, `max_days_per_month`, `max_days_per_year`, `carry_forward`, `requires_approval` | Master leave categories. |
| `LeavePolicy` | `LeavePolicy.js` | `LeavePolicy` | `leave_policies` | `name`, `leaves_config`, `applicable_roles`, `applicable_departments`, `effective_from` | Policy allocations. |
| `Leave` | `Leave.js` | `Leave` | `leaves` | `employeeId`, `leaveTypeId`, `startDate`, `endDate`, `totalDays`, `status`, `approvals` | Leave requests; automatic date calculation & ledger debit on approval. |
| `LeaveTransaction` | `LeaveTransaction.js` | `LeaveTransaction` | `leave_transactions` | `employeeId`, `leaveTypeId`, `type`, `quantity`, `sourceId`, `expiryDate` | Immutable credit/debit audit ledger. |
| `Regularization` | `Regularization.js` | `Regularization` | `regularizations` | `employeeId`, `attendanceId`, `requestedCheckIn`, `requestedCheckOut`, `status` | Clock correction workflow; updates `Attendance` upon approval. |
| `WFHRequest` | `WFHRequest.js` | `WFHRequest` | `wfh_requests` | `employeeId`, `startDate`, `endDate`, `status`, `reason` | Work-from-home requests; syncs `Attendance.status` to WFH. |
| `CompOffRequest` | `CompOffRequest.js` | `CompOffRequest` | `comp_off_requests` | `employeeId`, `workedDate`, `hoursWorked`, `status`, `expiryDate` | Compensatory off claims; issues 90-day credit transaction. |

## Axinix-Core Service Hooks (`backend_django/attendance/services.py`)
- **`LeaveService`**:
  - `before_create`: Validates date bounds, checks for overlapping active leaves for the same employee, automatically computes `totalDays`.
  - `after_update`: When status changes to `Approved`, records `LEAVE_DEBIT` in `LeaveTransaction` and marks `Attendance` as `On Leave` across date span.
- **`RegularizationService`**:
  - `before_create`: Rejects duplicate pending requests for the same attendance record.
  - `after_update`: When approved, atomically updates `Attendance.check_in` and `Attendance.check_out`.
- **`CompOffService`**:
  - `after_update`: When approved, credits `LeaveTransaction` with a 90-day expiry.
- **`WFHService`**:
  - `after_update`: When approved, updates `Attendance.status` to `Work From Home`.

## Dynamic API Usage
| File | Method | URL | Target Model |
|---|---|---|---|
| `index.jsx` | GET/POST/PUT | `/populate/:action/attendances` | `attendances` |
| `leave-regularization.jsx` | POST | `/populate/:action/leaves`, `/populate/:action/regularizations` | `leaves`, `regularizations` |
| `pending-approvals.jsx` | GET | `/populate/read/leaves`, `/populate/read/regularizations` | `leaves`, `regularizations` |
