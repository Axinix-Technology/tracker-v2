from django.db import models
from django.conf import settings
from populate_core.registry import register_model


# ============================================================================
# 1. SHIFTS & POLICIES
# ============================================================================

@register_model("shift", table_type="master", aliases=["shifts"])
class Shift(models.Model):
    name = models.CharField(max_length=64, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_period_mins = models.PositiveIntegerField(default=15)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shifts"

    def __str__(self):
        return self.name


@register_model("shift_assignment", table_type="transaction", aliases=["shift_assignments", "shiftassignments"])
class ShiftAssignment(models.Model):
    employeeId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="shift_assignments"
    )
    shiftId = models.ForeignKey(
        Shift,
        on_delete=models.CASCADE,
        db_column="shift_id",
        related_name="assignments"
    )
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(blank=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shift_assignments"
        indexes = [
            models.Index(fields=["status", "employeeId", "is_active"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def __str__(self):
        return f"{self.employeeId} -> {self.shiftId} ({self.start_date})"

    @property
    def employee(self):
        return self.employeeId

    @property
    def shift(self):
        return self.shiftId


@register_model("attendance_policy", table_type="master", aliases=["attendance_policies", "attendancepolicies"])
class AttendancePolicy(models.Model):
    name = models.CharField(max_length=128, unique=True)
    grace_period_mins = models.PositiveIntegerField(default=15)
    half_day_threshold_hours = models.FloatField(default=4.0)
    full_day_threshold_hours = models.FloatField(default=8.0)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_policies"

    def __str__(self):
        return self.name


# ============================================================================
# 2. DAILY ATTENDANCE
# ============================================================================

@register_model("attendance", table_type="transaction", aliases=["attendances"])
class Attendance(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="attendances"
    )
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=32, default="Present", db_index=True)
    check_in = models.TimeField(blank=True, null=True)
    check_out = models.TimeField(blank=True, null=True)
    work_hours = models.FloatField(default=0.0)
    overtime_hours = models.FloatField(default=0.0)
    shift = models.ForeignKey(
        Shift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendances"
        unique_together = ("employee", "date")
        indexes = [
            models.Index(fields=["status", "date"]),
            models.Index(fields=["employee", "date"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"

    @property
    def employeeId(self):
        return self.employee


@register_model("holiday", table_type="master", aliases=["holidays"])
class Holiday(models.Model):
    name = models.CharField(max_length=128)
    date = models.DateField(unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "holidays"

    def __str__(self):
        return f"{self.name} ({self.date})"


# ============================================================================
# 3. LEAVE TYPES & POLICIES
# ============================================================================

@register_model("leave_type", table_type="master", aliases=["leave_types", "leavetypes"])
class LeaveType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True, null=True)
    max_days_per_month = models.FloatField(default=2.0)
    max_days_per_year = models.FloatField(default=12.0)
    carry_forward = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "leave_types"
        indexes = [
            models.Index(fields=["status", "is_active", "name"]),
        ]

    def __str__(self):
        return self.name


@register_model("leave_policy", table_type="master", aliases=["leave_policies", "leavepolicy", "leavepolicies"])
class LeavePolicy(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    leaves_config = models.JSONField(default=list)
    applicable_roles = models.ManyToManyField("users.Role", blank=True, related_name="leave_policies")
    applicable_departments = models.ManyToManyField("users.Department", blank=True, related_name="leave_policies")
    applicable_designations = models.ManyToManyField("users.Designation", blank=True, related_name="leave_policies")
    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(blank=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    version = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "leave_policies"
        indexes = [
            models.Index(fields=["status", "is_active", "name"]),
        ]

    def __str__(self):
        return f"{self.name} (v{self.version})"


# ============================================================================
# 4. LEAVE REQUESTS & LEDGER
# ============================================================================

@register_model("leave", table_type="transaction", aliases=["leaves"])
class Leave(models.Model):
    employeeId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="leaves"
    )
    employeeName = models.CharField(max_length=255, blank=True, null=True, db_column="employee_name")
    departmentId = models.ForeignKey(
        "users.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="leaves"
    )
    leaveTypeId = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        db_column="leave_type_id",
        related_name="leaves"
    )
    leaveName = models.CharField(max_length=64, blank=True, null=True, db_column="leave_name")
    startDate = models.DateField(db_index=True, db_column="start_date")
    endDate = models.DateField(db_index=True, db_column="end_date")
    totalDays = models.FloatField(default=1.0, db_column="total_days")
    reason = models.TextField()
    status = models.CharField(max_length=32, default="Pending", db_index=True)
    metaStatus = models.CharField(max_length=32, default="active", db_index=True, db_column="meta_status")
    currentStepIndex = models.PositiveIntegerField(default=0, db_column="current_step_index")
    approvals = models.JSONField(default=list)
    managerId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="manager_id",
        related_name="managed_leaves"
    )
    managerComments = models.TextField(blank=True, null=True, db_column="manager_comments")
    approvedAt = models.DateTimeField(blank=True, null=True, db_column="approved_at")
    rejectedAt = models.DateTimeField(blank=True, null=True, db_column="rejected_at")
    document = models.CharField(max_length=512, blank=True, null=True)
    isEmergency = models.BooleanField(default=False, db_index=True, db_column="is_emergency")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "leaves"
        indexes = [
            models.Index(fields=["status", "employeeId", "startDate", "endDate"]),
            models.Index(fields=["status", "managerId", "startDate"]),
            models.Index(fields=["status", "departmentId", "startDate"]),
        ]

    def __str__(self):
        return f"{self.employeeId} - {self.leaveTypeId} ({self.startDate} to {self.endDate})"

    @property
    def employee(self):
        return self.employeeId

    @property
    def leave_type(self):
        return self.leaveTypeId


@register_model("leave_transaction", table_type="transaction", aliases=["leave_transactions", "leavetransaction"])
class LeaveTransaction(models.Model):
    employeeId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="leave_transactions"
    )
    leaveTypeId = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="leave_type_id",
        related_name="transactions"
    )
    type = models.CharField(max_length=64, db_index=True)
    sourceId = models.PositiveBigIntegerField(blank=True, null=True, db_index=True, db_column="source_id")
    sourceModel = models.CharField(max_length=64, blank=True, null=True, db_column="source_model")
    quantity = models.FloatField()
    description = models.TextField(blank=True, null=True)
    expiryDate = models.DateField(blank=True, null=True, db_index=True, db_column="expiry_date")
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "leave_transactions"
        indexes = [
            models.Index(fields=["status", "employeeId", "type"]),
            models.Index(fields=["status", "employeeId", "leaveTypeId"]),
        ]

    def __str__(self):
        return f"{self.employeeId} - {self.type}: {self.quantity}"

    @property
    def employee(self):
        return self.employeeId


# ============================================================================
# 5. REGULARIZATIONS & WORK REQUESTS
# ============================================================================

@register_model("regularization", table_type="transaction", aliases=["regularizations"])
class Regularization(models.Model):
    employeeId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="regularizations"
    )
    employeeName = models.CharField(max_length=255, blank=True, null=True, db_column="employee_name")
    departmentId = models.ForeignKey(
        "users.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="regularizations"
    )
    attendanceId = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        db_column="attendance_id",
        related_name="regularizations"
    )
    requestType = models.CharField(max_length=64, default="Regularization", db_index=True, db_column="request_type")
    requestDate = models.DateField(db_index=True, db_column="request_date")
    originalCheckIn = models.TimeField(blank=True, null=True, db_column="original_check_in")
    originalCheckOut = models.TimeField(blank=True, null=True, db_column="original_check_out")
    requestedCheckIn = models.TimeField(db_column="requested_check_in")
    requestedCheckOut = models.TimeField(db_column="requested_check_out")
    reason = models.TextField()
    status = models.CharField(max_length=32, default="Pending", db_index=True)
    metaStatus = models.CharField(max_length=32, default="active", db_index=True, db_column="meta_status")
    currentStepIndex = models.PositiveIntegerField(default=0, db_column="current_step_index")
    approvals = models.JSONField(default=list)
    managerId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="manager_id",
        related_name="managed_regularizations"
    )
    approvedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="approved_by",
        related_name="approved_regularizations"
    )
    approvedAt = models.DateTimeField(blank=True, null=True, db_column="approved_at")
    rejectedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="rejected_by",
        related_name="rejected_regularizations"
    )
    rejectedAt = models.DateTimeField(blank=True, null=True, db_column="rejected_at")
    approverComment = models.TextField(blank=True, null=True, db_column="approver_comment")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "regularizations"
        indexes = [
            models.Index(fields=["status", "employeeId", "requestDate"]),
            models.Index(fields=["status", "attendanceId"]),
        ]

    def __str__(self):
        return f"{self.employeeId} - Regularization on {self.requestDate}"

    @property
    def employee(self):
        return self.employeeId

    @property
    def attendance(self):
        return self.attendanceId


@register_model("wfh_request", table_type="transaction", aliases=["wfh_requests", "wfhrequest"])
class WFHRequest(models.Model):
    employeeId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="wfh_requests"
    )
    departmentId = models.ForeignKey(
        "users.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="wfh_requests"
    )
    startDate = models.DateField(db_index=True, db_column="start_date")
    endDate = models.DateField(db_index=True, db_column="end_date")
    reason = models.TextField()
    status = models.CharField(max_length=32, default="Pending", db_index=True)
    managerId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="manager_id",
        related_name="managed_wfh_requests"
    )
    approverComment = models.TextField(blank=True, null=True, db_column="approver_comment")
    currentStepIndex = models.PositiveIntegerField(default=0, db_column="current_step_index")
    approvals = models.JSONField(default=list)
    approvedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="approved_by",
        related_name="approved_wfh_requests"
    )
    approvedAt = models.DateTimeField(blank=True, null=True, db_column="approved_at")
    rejectedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="rejected_by",
        related_name="rejected_wfh_requests"
    )
    rejectedAt = models.DateTimeField(blank=True, null=True, db_column="rejected_at")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wfh_requests"
        indexes = [
            models.Index(fields=["status", "employeeId", "startDate", "endDate"]),
            models.Index(fields=["status", "departmentId", "startDate"]),
        ]

    def __str__(self):
        return f"{self.employeeId} - WFH ({self.startDate} to {self.endDate})"

    @property
    def employee(self):
        return self.employeeId


@register_model("comp_off_request", table_type="transaction", aliases=["comp_off_requests", "compoffrequest"])
class CompOffRequest(models.Model):
    employeeId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="comp_off_requests"
    )
    departmentId = models.ForeignKey(
        "users.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="department_id",
        related_name="comp_off_requests"
    )
    workedDate = models.DateField(db_index=True, db_column="worked_date")
    hoursWorked = models.FloatField(db_column="hours_worked")
    reason = models.TextField()
    status = models.CharField(max_length=32, default="Pending", db_index=True)
    managerId = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="manager_id",
        related_name="managed_comp_off_requests"
    )
    approverComment = models.TextField(blank=True, null=True, db_column="approver_comment")
    expiryDate = models.DateField(blank=True, null=True, db_index=True, db_column="expiry_date")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comp_off_requests"
        indexes = [
            models.Index(fields=["status", "employeeId", "workedDate"]),
            models.Index(fields=["status", "departmentId", "workedDate"]),
        ]

    def __str__(self):
        return f"{self.employeeId} - CompOff ({self.workedDate})"

    @property
    def employee(self):
        return self.employeeId


# ============================================================================
# 6. HOLIDAY OVERRIDES & SHORT PERMISSIONS
# ============================================================================

@register_model("holiday_override", table_type="master", aliases=["holiday_overrides", "holidayoverride"])
class HolidayOverride(models.Model):
    holiday = models.ForeignKey(
        Holiday,
        on_delete=models.CASCADE,
        related_name="overrides"
    )
    override_type = models.CharField(
        max_length=32,
        default="WORKING_DAY",
        choices=[("WORKING_DAY", "Working Day"), ("OPTIONAL_CANCELLED", "Optional Cancelled")]
    )
    scope = models.CharField(
        max_length=32,
        default="DEPARTMENT",
        choices=[
            ("GLOBAL", "Global"),
            ("LOCATION", "Location"),
            ("DEPARTMENT", "Department"),
            ("SHIFT", "Shift"),
            ("EMPLOYEE", "Employee")
        ]
    )
    target_id = models.PositiveBigIntegerField(null=True, blank=True, db_index=True)
    effective_date = models.DateField(db_index=True)
    compensation_policy = models.JSONField(default=dict)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_holiday_overrides"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "holiday_overrides"
        indexes = [
            models.Index(fields=["status", "scope", "target_id", "effective_date"]),
            models.Index(fields=["status", "holiday", "effective_date"]),
        ]

    def __str__(self):
        return f"Override {self.holiday} [{self.scope}:{self.target_id}] on {self.effective_date}"


@register_model("permission_balance", table_type="master", aliases=["permission_balances", "permissionbalance"])
class PermissionBalance(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="permission_balances"
    )
    year = models.PositiveIntegerField(db_index=True)
    month = models.PositiveSmallIntegerField(db_index=True)
    granted_hours = models.FloatField(default=2.0)
    carried_forward_hours = models.FloatField(default=0.0)
    used_hours = models.FloatField(default=0.0)
    expired_hours = models.FloatField(default=0.0)
    remaining_hours = models.FloatField(default=2.0)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permission_balances"
        constraints = [
            models.UniqueConstraint(fields=["employee", "year", "month"], name="uniq_emp_year_month_perm_balance")
        ]
        indexes = [
            models.Index(fields=["status", "employee", "year", "month"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}: {self.remaining_hours}h remaining"

    @property
    def employeeId(self):
        return self.employee


@register_model("permission_transaction", table_type="transaction", aliases=["permission_transactions", "permissiontransaction"])
class PermissionTransaction(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="permission_transactions"
    )
    date = models.DateField(db_index=True)
    duration_minutes = models.PositiveIntegerField()
    type = models.CharField(
        max_length=32,
        default="LATE_CHECKIN",
        choices=[
            ("LATE_CHECKIN", "Late Check-in"),
            ("EARLY_CHECKOUT", "Early Check-out"),
            ("PERSONAL_OUTING", "Personal Outing")
        ]
    )
    status = models.CharField(
        max_length=32,
        default="AutoConsumed",
        db_index=True,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
            ("AutoConsumed", "Auto Consumed")
        ]
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_permissions"
    )
    remarks = models.TextField(blank=True, null=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "permission_transactions"
        indexes = [
            models.Index(fields=["lifecycle_status", "employee", "date"]),
            models.Index(fields=["lifecycle_status", "status", "date"]),
        ]

    def __str__(self):
        return f"{self.employee} ({self.type}) {self.duration_minutes}m on {self.date}"

    @property
    def employeeId(self):
        return self.employee

    @property
    def durationMinutes(self):
        return self.duration_minutes
