from django.db import models
from django.conf import settings
from django.utils import timezone
from populate_core.registry import register_model


# ============================================================================
# 1. ASSET CATEGORY (MASTER)
# ============================================================================

@register_model("asset_category", table_type="master", aliases=["assets_categories"])
class AssetCategory(models.Model):
    name = models.CharField(max_length=128, unique=True, db_index=True)
    code = models.CharField(max_length=32, unique=True, db_index=True, help_text="Short code prefix defined by user in master, e.g. LAP, MOB, MON")
    description = models.TextField(blank=True, null=True)
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    warranty_months = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_asset_categories"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets_categories"
        indexes = [
            models.Index(fields=["status", "name"]),
            models.Index(fields=["status", "code"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


# ============================================================================
# 2. ASSET VENDOR (MASTER)
# ============================================================================

@register_model("asset_vendor", table_type="master", aliases=["assets_vendors"])
class AssetVendor(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    contact_person = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    gstin = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    address = models.JSONField(default=dict)
    vendor_status = models.CharField(max_length=32, default="Active", db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets_vendors"
        indexes = [
            models.Index(fields=["status", "name"]),
        ]

    def __str__(self):
        return self.name


# ============================================================================
# 3. ASSET PURCHASE (TRANSACTION)
# ============================================================================

@register_model("asset_purchase", table_type="transaction", aliases=["assets_purchases"])
class AssetPurchase(models.Model):
    vendor = models.ForeignKey(
        AssetVendor,
        on_delete=models.PROTECT,
        related_name="purchases"
    )
    po_number = models.CharField(max_length=64, unique=True, db_index=True)
    purchase_date = models.DateField(default=timezone.now, db_index=True)
    purchase_status = models.CharField(max_length=32, default="Draft", db_index=True)  # Draft, Pending Approval, Approved, Received, Cancelled
    items = models.JSONField(default=list)  # [{ "category_id": int, "name": str, "model": str, "serial_number_prefix": str, "quantity": int, "unit_price": float, "tax_rate": float }]
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=32, default="Unpaid", db_index=True)  # Unpaid, Partially Paid, Paid
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_asset_purchases"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets_purchases"
        indexes = [
            models.Index(fields=["status", "purchase_status", "purchase_date"]),
        ]

    def __str__(self):
        return f"{self.po_number} ({self.purchase_status})"


# ============================================================================
# 4. ASSET (MASTER REGISTER)
# ============================================================================

@register_model("asset", table_type="master", aliases=["assets"])
class Asset(models.Model):
    asset_id = models.CharField(max_length=64, unique=True, db_index=True, blank=True)
    category = models.ForeignKey(
        AssetCategory,
        on_delete=models.PROTECT,
        related_name="assets"
    )
    name = models.CharField(max_length=255, db_index=True)
    serial_number = models.CharField(max_length=128, unique=True, null=True, blank=True, db_index=True)
    imei = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    make = models.CharField(max_length=128, blank=True, null=True)
    model = models.CharField(max_length=128, blank=True, null=True)
    
    purchase = models.ForeignKey(
        AssetPurchase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_assets"
    )
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    vendor_name = models.CharField(max_length=255, blank=True, null=True)
    invoice_number = models.CharField(max_length=128, blank=True, null=True)
    invoice_file = models.CharField(max_length=512, blank=True, null=True)
    warranty_expiry = models.DateField(null=True, blank=True, db_index=True)
    storage_location = models.CharField(max_length=255, blank=True, null=True)
    
    asset_status = models.CharField(max_length=32, default="Available", db_index=True)  # Available, Allocated, Under Repair, Reserved, Lost, Disposed
    meta_status = models.CharField(max_length=32, default="active", db_index=True)  # active, inactive, archive
    
    condition = models.CharField(max_length=32, default="Good", db_index=True)  # Excellent, Good, Fair, Poor, Damaged
    condition_last_assessed_at = models.DateTimeField(null=True, blank=True)
    condition_last_assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assessed_assets"
    )
    condition_notes = models.TextField(blank=True, null=True)
    
    current_allocated_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="allocated_assets"
    )
    current_allocation_id = models.PositiveBigIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assets"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets"
        indexes = [
            models.Index(fields=["status", "asset_status", "created_at"]),
            models.Index(fields=["status", "category", "asset_status"]),
            models.Index(fields=["status", "current_allocated_to", "asset_status"]),
            models.Index(fields=["status", "condition"]),
        ]

    def __str__(self):
        return f"{self.asset_id} - {self.name} ({self.asset_status})"


# ============================================================================
# 5. ASSET ALLOCATION (TRANSACTION)
# ============================================================================

@register_model("asset_allocation", table_type="transaction", aliases=["assets_allocations"])
class AssetAllocation(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name="allocations"
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="asset_allocations"
    )
    department = models.ForeignKey(
        "users.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_allocations"
    )
    allocation_type = models.CharField(max_length=32, default="Allocation", db_index=True)  # Allocation, Transfer, Temporary
    allocation_date = models.DateField(default=timezone.now, db_index=True)
    expected_return = models.DateField(null=True, blank=True)
    actual_return = models.DateField(null=True, blank=True)
    
    returned_condition = models.CharField(max_length=32, blank=True, null=True)  # Excellent, Good, Fair, Poor, Damaged, Lost
    return_notes = models.TextField(blank=True, null=True)
    
    transfer_from_employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transferred_out_allocations"
    )
    transfer_to_employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transferred_in_allocations"
    )
    
    allocation_status = models.CharField(max_length=32, default="Pending Approval", db_index=True)  # Pending Approval, Active, Returned, Transferred, Rejected
    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    approvals = models.JSONField(default=list)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_asset_allocations"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets_allocations"
        indexes = [
            models.Index(fields=["status", "allocation_status", "allocation_date"]),
            models.Index(fields=["status", "employee", "allocation_status"]),
            models.Index(fields=["status", "asset", "allocation_status"]),
        ]

    def __str__(self):
        return f"Alloc {self.asset} -> {self.employee} ({self.allocation_status})"


# ============================================================================
# 6. ASSET INCIDENT (TRANSACTION)
# ============================================================================

@register_model("asset_incident", table_type="transaction", aliases=["assets_incidents"])
class AssetIncident(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name="incidents"
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reported_asset_incidents"
    )
    department = models.ForeignKey(
        "users.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_incidents"
    )
    allocation = models.ForeignKey(
        AssetAllocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incidents"
    )
    incident_type = models.CharField(max_length=32, db_index=True)  # Damage, Theft, Loss, Negligence
    incident_date = models.DateField(default=timezone.now, db_index=True)
    description = models.TextField()
    
    estimated_repair_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    recovery_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    recovery_approved = models.BooleanField(default=False)
    recovery_deducted_in_payroll = models.BooleanField(default=False)
    recovery_payroll_id = models.PositiveBigIntegerField(null=True, blank=True)
    
    incident_status = models.CharField(max_length=32, default="Reported", db_index=True)  # Reported, Under Investigation, Approved, Rejected, Closed
    approvals = models.JSONField(default=list)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_asset_incidents"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets_incidents"
        indexes = [
            models.Index(fields=["status", "incident_status", "incident_date"]),
            models.Index(fields=["status", "asset", "incident_type"]),
        ]

    def __str__(self):
        return f"Incident: {self.incident_type} on {self.asset} ({self.incident_status})"


# ============================================================================
# 7. ASSET REPAIR (TRANSACTION)
# ============================================================================

@register_model("asset_repair", table_type="transaction", aliases=["assets_repairs"])
class AssetRepair(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name="repairs"
    )
    incident = models.ForeignKey(
        AssetIncident,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="repairs"
    )
    vendor_name = models.CharField(max_length=255, blank=True, null=True)
    vendor_contact = models.CharField(max_length=128, blank=True, null=True)
    repair_description = models.TextField(blank=True, null=True)
    
    sent_date = models.DateField(default=timezone.now, db_index=True)
    expected_return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    repair_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    repair_condition = models.CharField(max_length=32, default="Good")  # Excellent, Good, Fair, Poor, Damaged
    repair_status = models.CharField(max_length=32, default="Sent for Repair", db_index=True)  # Sent for Repair, In Repair, Repaired, Beyond Repair
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_asset_repairs"
    )
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets_repairs"
        indexes = [
            models.Index(fields=["status", "repair_status", "sent_date"]),
            models.Index(fields=["status", "asset", "repair_status"]),
        ]

    def __str__(self):
        return f"Repair: {self.asset} ({self.repair_status})"


# ============================================================================
# 8. ASSET STOCK LEDGER (AUDIT LEDGER)
# ============================================================================

@register_model(
    "asset_stock_ledger",
    table_type="ledger",
    aliases=["assets_stock_ledgers"],
    allow_direct_create=False,
    allow_direct_update=False,
    allow_direct_delete=False
)
class AssetStockLedger(models.Model):
    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name="stock_ledger_entries"
    )
    transaction_type = models.CharField(max_length=8, db_index=True)  # IN, OUT, TRANSFER
    trigger_type = models.CharField(max_length=64, db_index=True)  # Purchase_Receipt, Employee_Return, Repair_Return, Employee_Allocation, Send_To_Repair, Write_Off_Disposal
    previous_state = models.CharField(max_length=32, blank=True, null=True)
    new_state = models.CharField(max_length=32, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_asset_transactions"
    )
    reference_model = models.CharField(max_length=64, blank=True, null=True)
    reference_id = models.PositiveBigIntegerField(null=True, blank=True)
    transaction_date = models.DateTimeField(default=timezone.now, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "assets_stock_ledgers"
        indexes = [
            models.Index(fields=["status", "transaction_date"]),
            models.Index(fields=["status", "asset", "transaction_date"]),
            models.Index(fields=["status", "trigger_type"]),
        ]

    def __str__(self):
        return f"Ledger: {self.transaction_type} - {self.trigger_type} ({self.asset_id})"


# ============================================================================
# 9. ASSET INVOICE (VENDOR INVOICE)
# ============================================================================

@register_model("asset_invoice", table_type="transaction", aliases=["assets_invoices"])
class AssetInvoice(models.Model):
    purchase = models.ForeignKey(
        AssetPurchase,
        on_delete=models.CASCADE,
        related_name="invoices"
    )
    invoice_number = models.CharField(max_length=128, unique=True, db_index=True)
    invoice_date = models.DateField()
    due_date = models.DateField(db_index=True)
    sub_total = models.DecimalField(max_digits=14, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=32, default="Pending", db_index=True)  # Pending, Approved, Paid, Void
    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets_invoices"
        indexes = [
            models.Index(fields=["status", "due_date"]),
            models.Index(fields=["purchase", "status"]),
            models.Index(fields=["lifecycle_status", "status", "created_at"]),
        ]
        ordering = ["-invoice_date", "-id"]

    def __str__(self):
        return f"Asset Invoice {self.invoice_number} ({self.status}) - {self.total_amount}"


# ============================================================================
# 10. ASSET PAYMENT (VENDOR PAYMENT)
# ============================================================================

@register_model("asset_payment", table_type="transaction", aliases=["assets_payments"])
class AssetPayment(models.Model):
    invoice = models.ForeignKey(
        AssetInvoice,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    payment_date = models.DateField(default=timezone.now, db_index=True)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2)
    payment_mode = models.CharField(max_length=64, default="Bank Transfer")  # Cash, Bank Transfer, Cheque, UPI, Credit Card
    transaction_ref = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    status = models.CharField(max_length=32, default="Success", db_index=True)  # Pending, Success, Failed
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assets_payments"
        indexes = [
            models.Index(fields=["invoice", "status"]),
            models.Index(fields=["payment_date", "status"]),
            models.Index(fields=["lifecycle_status", "status", "payment_date"]),
        ]
        ordering = ["-payment_date", "-id"]

    def __str__(self):
        return f"Asset Payment #{self.id} for Invoice #{self.invoice_id}: {self.amount_paid}"
