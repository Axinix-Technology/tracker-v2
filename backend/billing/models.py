from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from populate_core.registry import register_model


# ============================================================================
# 1. QUOTATION
# ============================================================================

@register_model(
    "quotation",
    table_type="transaction",
    aliases=["quotations"],
    search_fields=["quotation_number", "client__name", "notes"],
    status_field="lifecycle_status",
    public_fields=[]
)
class Quotation(models.Model):
    quotation_number = models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True)
    client = models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='quotations', db_index=True)
    opportunity_id = models.IntegerField(null=True, blank=True, db_index=True)
    contact_id = models.IntegerField(null=True, blank=True, db_index=True)

    line_items = models.JSONField(default=list, help_text="List of line items: description, qty, unitPrice, discount, taxRate, lineTotal")

    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_tax = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_discount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    valid_until = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    terms_and_conditions = models.TextField(blank=True, null=True)

    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='prepared_quotations', db_index=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_quotations')

    status = models.CharField(
        max_length=64,
        default='Draft',
        db_index=True,
        help_text="Draft, Sent, Under Review, Revision Requested, Internally Approved, Client Approved, Client Rejected, Expired, Converted to Order"
    )
    meta_status = models.CharField(max_length=32, default='active', db_index=True)
    lifecycle_status = models.IntegerField(default=1, db_index=True, help_text="1=Active, 0=Deleted (Recipe 02 soft-delete)")

    revision_number = models.IntegerField(default=1)
    parent_quotation = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='child_quotations')

    approval_history = models.JSONField(default=list, help_text="History of approval actions: action, by, at, remarks")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_quotations"
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["lifecycle_status", "client", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.quotation_number or 'Draft'} - {self.client.name} (v{self.revision_number})"


# ============================================================================
# 2. QUOTATION REVISION (IMMUTABLE SNAPSHOT)
# ============================================================================

@register_model(
    "quotation_revision",
    table_type="ledger",
    aliases=["quotation_revisions", "quotationrevisions"],
    search_fields=["change_reason"],
    status_field="status",
    allow_direct_update=False,
    allow_direct_delete=False
)
class QuotationRevision(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='revisions', db_index=True)
    revision_number = models.IntegerField()
    snapshot = models.JSONField(help_text="Immutable state snapshot of quotation at time of revision")
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='quotation_revisions')
    change_reason = models.TextField(blank=True, null=True)

    status = models.IntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "billing_quotation_revisions"
        indexes = [
            models.Index(fields=["quotation", "revision_number"]),
            models.Index(fields=["status", "quotation", "-created_at"]),
        ]
        ordering = ["quotation", "-revision_number"]

    def __str__(self):
        return f"Quote #{self.quotation_id} Rev {self.revision_number}"


# ============================================================================
# 3. ORDER ACKNOWLEDGEMENT (CONTRACT / OA)
# ============================================================================

@register_model(
    "order_acknowledgement",
    table_type="transaction",
    aliases=["order_acknowledgements", "orderacknowledgements", "orderacknowledgments", "oa"],
    search_fields=["order_number", "client__name"],
    status_field="lifecycle_status",
    public_fields=[]
)
class OrderAcknowledgement(models.Model):
    order_number = models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True)
    quotation = models.ForeignKey(Quotation, null=True, blank=True, on_delete=models.SET_NULL, related_name='order_acknowledgements', db_index=True)
    opportunity_id = models.IntegerField(null=True, blank=True, db_index=True)
    client = models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='order_acknowledgements', db_index=True)

    modules = models.JSONField(default=list, help_text="Line items: projectTypeId, serviceProviderId, agreedValue, description")
    total_order_value = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    client_approval = models.JSONField(default=dict, help_text="Client signature / approval record: approvedBy, approvedAt, remarks, signatureRef")
    internal_approval = models.JSONField(default=dict, help_text="Internal company approval: approvedBy, approvedAt, remarks")

    status = models.CharField(
        max_length=64,
        default='Pending Internal Approval',
        db_index=True,
        help_text="Pending Internal Approval, Pending Client Approval, Client Approved, Active, Completed, Cancelled"
    )
    meta_status = models.CharField(max_length=32, default='active', db_index=True)
    lifecycle_status = models.IntegerField(default=1, db_index=True)

    sales_person = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales_orders', db_index=True)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='completed_orders', db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_order_acknowledgements"
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["lifecycle_status", "client", "created_at"]),
            models.Index(fields=["sales_person", "status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_number or 'Draft'} - {self.client.name}"


# ============================================================================
# 4. INVOICE (CLIENT INVOICE)
# ============================================================================

@register_model(
    "invoice",
    table_type="transaction",
    aliases=["invoices"],
    search_fields=["invoice_number", "client__name", "gstin"],
    status_field="lifecycle_status",
    public_fields=[]
)
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=64, unique=True, db_index=True)
    client = models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='invoices', db_index=True)
    contract = models.ForeignKey(OrderAcknowledgement, null=True, blank=True, on_delete=models.SET_NULL, related_name='invoices', db_index=True)
    quotation = models.ForeignKey(Quotation, null=True, blank=True, on_delete=models.SET_NULL, related_name='invoices', db_index=True)
    opportunity_id = models.IntegerField(null=True, blank=True, db_index=True)

    issue_date = models.DateField(default=timezone.now, db_index=True)
    due_date = models.DateField(db_index=True)
    currency = models.CharField(max_length=16, default='INR')

    line_items = models.JSONField(default=list, help_text="Line items: productId, description, quantity, unitPrice, taxRate, discount, amount")

    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    balance_due = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(
        max_length=32,
        default='Draft',
        db_index=True,
        help_text="Draft, Issued, Partially Paid, Paid, Overdue, Cancelled"
    )
    payment_milestone_id = models.IntegerField(null=True, blank=True, db_index=True)
    gstin = models.CharField(max_length=64, blank=True, null=True)
    billing_address = models.JSONField(default=dict, help_text="Street, city, state, zip, country")

    notes = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)

    meta_status = models.CharField(max_length=32, default='active', db_index=True)
    lifecycle_status = models.IntegerField(default=1, db_index=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_invoices')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_invoices"
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["status", "due_date"]),
            models.Index(fields=["lifecycle_status", "client", "issue_date"]),
            models.Index(fields=["contract", "status"]),
        ]
        ordering = ["-issue_date", "-id"]

    def __str__(self):
        return f"{self.invoice_number} ({self.client.name}) - {self.total_amount} {self.currency}"


# ============================================================================
# 5. PAYMENT (CLIENT PAYMENT RECEIPT)
# ============================================================================

@register_model(
    "payment",
    table_type="transaction",
    aliases=["payments"],
    search_fields=["reference_no", "client__name"],
    status_field="lifecycle_status",
    public_fields=[]
)
class Payment(models.Model):
    client = models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='payments', db_index=True)
    oa = models.ForeignKey(OrderAcknowledgement, null=True, blank=True, on_delete=models.SET_NULL, related_name='payments', db_index=True)
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, related_name='payments', db_index=True)

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_date = models.DateField(default=timezone.now, db_index=True)
    payment_method = models.CharField(max_length=64, default='Bank Transfer')
    reference_no = models.CharField(max_length=128, blank=True, null=True, db_index=True)

    status = models.CharField(max_length=32, default='Confirmed', db_index=True)  # Pending, Confirmed, Failed
    notes = models.TextField(blank=True, null=True)
    attachments = models.JSONField(default=list)

    lifecycle_status = models.IntegerField(default=1, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='recorded_payments')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_payments"
        indexes = [
            models.Index(fields=["client", "-payment_date"]),
            models.Index(fields=["lifecycle_status", "client", "payment_date"]),
        ]
        ordering = ["-payment_date", "-id"]

    def __str__(self):
        return f"Payment #{self.id} - {self.client.name}: {self.amount}"


# ============================================================================
# 6. PAYMENT JOURNAL (RECEIPT VOUCHER / VERIFICATION JOURNAL)
# ============================================================================

@register_model(
    "payment_journal",
    table_type="transaction",
    aliases=["payment_journals", "paymentjournals"],
    search_fields=["receipt_number", "reference_number", "client__name", "bank_name"],
    status_field="lifecycle_status",
    public_fields=[]
)
class PaymentJournal(models.Model):
    receipt_number = models.CharField(max_length=64, unique=True, db_index=True)
    client = models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='payment_journals', db_index=True)
    order = models.ForeignKey(OrderAcknowledgement, null=True, blank=True, on_delete=models.SET_NULL, related_name='payment_journals', db_index=True)

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_date = models.DateField(default=timezone.now, db_index=True)
    payment_mode = models.CharField(max_length=64, default='Bank Transfer')
    reference_number = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    bank_name = models.CharField(max_length=128, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)
    attachments = models.JSONField(default=list)

    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='received_journals')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_journals')

    status = models.CharField(max_length=32, default='Draft', db_index=True)  # Draft, Verified, Cancelled
    meta_status = models.CharField(max_length=32, default='active', db_index=True)
    lifecycle_status = models.IntegerField(default=1, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_payment_journals"
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["-payment_date", "status"]),
            models.Index(fields=["lifecycle_status", "client", "created_at"]),
        ]
        ordering = ["-payment_date", "-id"]

    def __str__(self):
        return f"{self.receipt_number} - {self.client.name}: {self.amount}"


# ============================================================================
# 7. CLIENT LEDGER (IMMUTABLE DOUBLE-ENTRY AUDIT LEDGER)
# ============================================================================

@register_model(
    "client_ledger",
    table_type="ledger",
    aliases=["client_ledgers", "clients_ledgers", "clients_ledger", "clientledger"],
    search_fields=["description", "narration", "client__name"],
    status_field="status",
    allow_direct_update=False,
    allow_direct_delete=False
)
class ClientLedger(models.Model):
    client = models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='ledger_entries', db_index=True)
    date = models.DateTimeField(default=timezone.now, db_index=True)

    type = models.CharField(max_length=16, db_index=True, help_text="Credit (Receipt) or Debit (Invoice/Charge)")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    running_balance = models.DecimalField(max_digits=14, decimal_places=2)

    reference_model = models.CharField(max_length=64, db_index=True, help_text="order_acknowledgements, payment_journals, invoices, payments")
    reference_id = models.IntegerField(db_index=True)

    description = models.TextField(blank=True, null=True)
    narration = models.TextField(blank=True, null=True)

    entry_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='client_ledger_entries')

    status = models.IntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "billing_client_ledgers"
        indexes = [
            models.Index(fields=["client", "-date"]),
            models.Index(fields=["reference_model", "reference_id"]),
            models.Index(fields=["status", "client", "date"]),
        ]
        ordering = ["client", "-date", "-id"]

    def __str__(self):
        return f"Ledger #{self.id} [{self.type}] {self.client.name}: {self.amount} (Bal: {self.running_balance})"


# ============================================================================
# 8. PERIOD CLOSURE (FINANCIAL PERIOD LOCK)
# ============================================================================

@register_model(
    "period_closure",
    table_type="transaction",
    aliases=["period_closures", "periodclosures"],
    search_fields=["period_label", "financial_year_label", "closure_remarks"],
    status_field="lifecycle_status",
    public_fields=[]
)
class PeriodClosure(models.Model):
    period_label = models.CharField(max_length=128, help_text="e.g. 'April 2026', 'Q1 FY2026-27'")
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    financial_year_label = models.CharField(max_length=64, db_index=True, help_text="e.g. 'FY2026-27'")

    status = models.CharField(max_length=32, default='Open', db_index=True, help_text="Open, In Progress, Closed, Reopened")

    modules = models.JSONField(
        default=dict,
        help_text="Granular module closure locks: payroll, attendance, expenses, timeTracking, quotations"
    )
    summary = models.JSONField(
        default=dict,
        help_text="Summary statistics computed at closure time for audit trail"
    )

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_period_closures')
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='finalized_period_closures')
    closed_at = models.DateTimeField(null=True, blank=True)
    closure_remarks = models.TextField(blank=True, null=True)

    reopened_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reopened_period_closures')
    reopened_at = models.DateTimeField(null=True, blank=True)
    reopen_reason = models.TextField(blank=True, null=True)

    lifecycle_status = models.IntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_period_closures"
        indexes = [
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["status", "-start_date"]),
            models.Index(fields=["financial_year_label", "start_date"]),
            models.Index(fields=["lifecycle_status", "status", "start_date"]),
        ]
        ordering = ["-start_date"]

    def __str__(self):
        return f"Period {self.period_label} ({self.status})"

