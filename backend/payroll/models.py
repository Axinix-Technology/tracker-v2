from django.db import models
from django.conf import settings
from django.utils import timezone
from populate_core.registry import register_model


# ============================================================================
# 1. SALARY STRUCTURE (COMPENSATION DEFINITIONS & VERSIONING)
# ============================================================================

@register_model(
    "salary_structure",
    table_type="master",
    aliases=["salary_structures", "salarystructure"]
)
class SalaryStructure(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="salary_structures"
    )
    version = models.PositiveIntegerField(default=1)
    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(null=True, blank=True, db_index=True)
    ctc = models.DecimalField(max_digits=12, decimal_places=2)
    earnings = models.JSONField(default=list)     # [{ "code": str, "name": str, "type": "fixed"|"variable"|"percentage_of_basic", "amount": float, "taxable": bool, "isProratable": bool }]
    deductions = models.JSONField(default=list)   # [{ "code": str, "name": str, "type": "fixed"|"percentage_of_basic"|"percentage_of_gross"|"statutory", "amount": float, "ceiling": float }]
    pf_employee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=12.0)
    pf_ceiling = models.DecimalField(max_digits=10, decimal_places=2, default=15000.0)
    esi_applicable = models.BooleanField(default=True)
    overtime_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_salary_structures"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "salary_structures"
        indexes = [
            models.Index(fields=["status", "employee", "effective_from"]),
            models.Index(fields=["status", "employee", "version"]),
        ]

    def __str__(self):
        return f"{self.employee} - Salary v{self.version} (CTC: {self.ctc})"

    @property
    def employeeId(self):
        return self.employee

    @property
    def effectiveFrom(self):
        return self.effective_from

    @property
    def effectiveTo(self):
        return self.effective_to

    @property
    def pfEmployeePercent(self):
        return self.pf_employee_percent

    @property
    def pfCeiling(self):
        return self.pf_ceiling

    @property
    def esiApplicable(self):
        return self.esi_applicable

    @property
    def overtimeRate(self):
        return self.overtime_rate

    @property
    def createdBy(self):
        return self.created_by


# ============================================================================
# 2. PAYROLL RUN (BATCH DISBURSEMENT RUNS)
# ============================================================================

@register_model(
    "payroll_run",
    table_type="transaction",
    aliases=["payroll_runs", "payrollrun"]
)
class PayrollRun(models.Model):
    RUN_STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Processing", "Processing"),
        ("Computed", "Computed"),
        ("Approved", "Approved"),
        ("Paid", "Paid"),
    ]

    month = models.PositiveSmallIntegerField()  # 1-12
    year = models.PositiveIntegerField()
    run_status = models.CharField(
        max_length=32,
        choices=RUN_STATUS_CHOICES,
        default="Draft",
        db_index=True
    )
    employee_ids = models.JSONField(default=list)  # list of employee PKs
    payroll_ids = models.JSONField(default=list)   # list of generated payroll PKs
    total_employees = models.PositiveIntegerField(default=0)
    processed_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    total_gross = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    total_net = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiated_payroll_runs"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_payroll_runs"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    audit_events = models.JSONField(default=list)  # [{ "event": str, "performedBy": int, "timestamp": iso, "note": str }]
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payroll_runs"
        indexes = [
            models.Index(fields=["status", "year", "month"]),
            models.Index(fields=["status", "run_status", "created_at"]),
        ]

    def __str__(self):
        return f"Payroll Run {self.month}/{self.year} ({self.run_status})"

    @property
    def totalEmployees(self):
        return self.total_employees

    @property
    def processedCount(self):
        return self.processed_count

    @property
    def failedCount(self):
        return self.failed_count

    @property
    def totalGross(self):
        return self.total_gross

    @property
    def totalNet(self):
        return self.total_net

    @property
    def initiatedBy(self):
        return self.initiated_by

    @property
    def approvedBy(self):
        return self.approved_by

    @property
    def approvedAt(self):
        return self.approved_at

    @property
    def paidAt(self):
        return self.paid_at

    @property
    def payrollAuditEvents(self):
        return self.audit_events


# ============================================================================
# 3. PAYROLL (INDIVIDUAL MONTHLY PAYSLIP LEDGER)
# ============================================================================

@register_model(
    "payroll",
    table_type="transaction",
    aliases=["payrolls", "payslips", "payslip"]
)
class Payroll(models.Model):
    PAYROLL_STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Processing", "Processing"),
        ("Processed", "Processed"),
        ("Approved", "Approved"),
        ("Paid", "Paid"),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payrolls"
    )
    department = models.ForeignKey(
        "users.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payrolls"
    )
    month = models.PositiveSmallIntegerField(db_index=True)  # 1-12
    year = models.PositiveIntegerField(db_index=True)
    salary_structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payrolls"
    )
    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payrolls"
    )
    working_days = models.FloatField(default=0.0)
    present_days = models.FloatField(default=0.0)
    lop_days = models.FloatField(default=0.0)
    leave_days = models.FloatField(default=0.0)
    overtime_hours = models.FloatField(default=0.0)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    earned_breakdown = models.JSONField(default=dict)      # { "BASIC": float, "HRA": float, ... }
    deduction_breakdown = models.JSONField(default=dict)   # { "PF_EE": float, "ESI_EE": float, ... }
    pf_employer_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    esi_employer_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payroll_status = models.CharField(
        max_length=32,
        choices=PAYROLL_STATUS_CHOICES,
        default="Draft",
        db_index=True
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_payrolls"
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_individual_payrolls"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    frozen_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    payslip_url = models.CharField(max_length=512, blank=True, null=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payrolls"
        constraints = [
            models.UniqueConstraint(fields=["employee", "month", "year"], name="uniq_emp_month_year_payroll")
        ]
        indexes = [
            models.Index(fields=["status", "month", "year"]),
            models.Index(fields=["status", "department", "month", "year"]),
            models.Index(fields=["status", "payroll_status"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}: Net {self.net_salary} ({self.payroll_status})"

    @property
    def employeeId(self):
        return self.employee

    @property
    def departmentId(self):
        return self.department

    @property
    def salaryStructureId(self):
        return self.salary_structure

    @property
    def payrollRunId(self):
        return self.payroll_run

    @property
    def workingDays(self):
        return self.working_days

    @property
    def presentDays(self):
        return self.present_days

    @property
    def lopDays(self):
        return self.lop_days

    @property
    def leaveDays(self):
        return self.leave_days

    @property
    def overtimeHours(self):
        return self.overtime_hours

    @property
    def overtimePay(self):
        return self.overtime_pay

    @property
    def earnedBreakdown(self):
        return self.earned_breakdown

    @property
    def deductionBreakdown(self):
        return self.deduction_breakdown

    @property
    def pfEmployerContribution(self):
        return self.pf_employer_contribution

    @property
    def esiEmployerContribution(self):
        return self.esi_employer_contribution

    @property
    def grossSalary(self):
        return self.gross_salary

    @property
    def netSalary(self):
        return self.net_salary

    @property
    def payslipUrl(self):
        return self.payslip_url


# ============================================================================
# 4. EXPENSE (REIMBURSEMENTS & GST LEDGER)
# ============================================================================

@register_model(
    "expense",
    table_type="transaction",
    aliases=["expenses"]
)
class Expense(models.Model):
    EXPENSE_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("reimbursed", "Reimbursed"),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses"
    )
    client = models.ForeignKey(
        "users.Client",
        on_delete=models.CASCADE,
        related_name="expenses"
    )
    project_type = models.ForeignKey(
        "users.ProjectType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses"
    )
    is_billable = models.BooleanField(default=False, db_index=True)
    date = models.DateField(db_index=True)
    expense_period = models.CharField(max_length=16, db_index=True)  # 'YYYY-MM'
    expenses = models.JSONField(default=list)  # [{ "expenseType": "travel"|"accommodation"|"miscellaneous"|"food", "amount": float, "description": str, "isGSTApplicable": bool, "gstAmount": float, "attachments": [] }]
    day_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_expenses = models.PositiveIntegerField(default=0)
    expense_status = models.CharField(
        max_length=32,
        choices=EXPENSE_STATUS_CHOICES,
        default="pending",
        db_index=True
    )
    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_expenses"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_expenses"
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    reimbursed_at = models.DateTimeField(null=True, blank=True)
    reimbursed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reimbursed_expenses"
    )
    submitted_at = models.DateTimeField(default=timezone.now)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "expenses"
        indexes = [
            models.Index(fields=["status", "employee", "date"]),
            models.Index(fields=["status", "client", "expense_status"]),
            models.Index(fields=["status", "expense_period"]),
            models.Index(fields=["status", "project_type", "expense_status"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.date}: {self.day_total} ({self.expense_status})"

    @property
    def employeeId(self):
        return self.employee

    @property
    def clientId(self):
        return self.client

    @property
    def projectTypeId(self):
        return self.project_type

    @property
    def isBillable(self):
        return self.is_billable

    @property
    def expensePeriod(self):
        return self.expense_period

    @property
    def dayTotal(self):
        return self.day_total

    @property
    def totalExpenses(self):
        return self.total_expenses

    @property
    def approvedBy(self):
        return self.approved_by

    @property
    def reimbursedAt(self):
        return self.reimbursed_at

