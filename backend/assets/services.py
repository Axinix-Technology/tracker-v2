import logging
from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone
from populate_core.registry import BaseService, register_service
from populate_core.response.exceptions import AuthorizationError, ValidationError, NotFoundError

logger = logging.getLogger("assets.services")


def write_stock_ledger(
    asset,
    transaction_type,
    trigger_type,
    previous_state="",
    new_state="",
    quantity=1,
    performed_by=None,
    reference_model="",
    reference_id=None
):
    """
    Append-only inventory audit ledger recorder.
    Executes within the caller's transaction.atomic block.
    NEVER silently swallows exceptions: if ledger write fails, the entire business operation rolls back.
    """
    from .models import AssetStockLedger
    ledger = AssetStockLedger.objects.create(
        asset=asset,
        transaction_type=transaction_type,
        trigger_type=trigger_type,
        previous_state=previous_state,
        new_state=new_state,
        quantity=quantity,
        performed_by=performed_by,
        reference_model=reference_model,
        reference_id=reference_id,
        transaction_date=timezone.now()
    )
    logger.info(f"[StockLedger] {transaction_type} ({trigger_type}) on asset {asset.asset_id} recorded (ID: {ledger.id}).")
    return ledger


# ============================================================================
# 1. ASSET CATEGORY SERVICE
# ============================================================================

@register_service("asset_category")
class AssetCategoryService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def before_create(self, context, data):
        if not data.get("name"):
            raise ValueError("Category name is required.")

        # User explicitly configures the short code in the master
        code = str(data.get("code") or "").strip().upper()
        if not code:
            raise ValueError("Category short code (e.g. LAP, MOB, MON) is required in the master.")
        data["code"] = code

        user = getattr(context, "user", None)
        if user and user.is_authenticated:
            data["created_by_id"] = user.id

        data["is_active"] = data.get("is_active", True)
        data["status"] = data.get("status", 1)
        return data

    def before_update(self, context, instance, data):
        if "code" in data:
            data["code"] = str(data["code"]).strip().upper()
        data.pop("created_by", None)
        data.pop("created_by_id", None)
        return data


# ============================================================================
# 2. ASSET VENDOR SERVICE
# ============================================================================

@register_service("asset_vendor")
class AssetVendorService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def before_create(self, context, data):
        if not data.get("name"):
            raise ValueError("Vendor name is required.")
        data["status"] = data.get("status", 1)
        return data


# ============================================================================
# 3. ASSET SERVICE (MASTER REGISTER)
# ============================================================================

@register_service("asset")
class AssetService(BaseService):
    ALLOWED_TRANSITIONS = {
        "Available": ["Reserved", "Under Repair", "Lost", "Disposed"],
        "Reserved": ["Available", "Allocated", "Disposed"],
        "Allocated": ["Available", "Under Repair", "Lost"],
        "Under Repair": ["Available", "Disposed"],
        "Lost": ["Disposed"],
        "Disposed": []
    }

    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def before_create(self, context, data):
        from .models import Asset, AssetCategory

        category_id = data.get("category") or data.get("category_id")
        if not category_id:
            raise ValueError("category is required for Asset registration.")

        with transaction.atomic():
            # Concurrency protection: Lock the category row while computing sequence
            try:
                category = AssetCategory.objects.select_for_update().get(id=category_id, is_active=True, status=1)
            except AssetCategory.DoesNotExist:
                raise NotFoundError(f"Active asset category #{category_id} not found.")

            category_code = (category.code or "").strip().upper()
            if not category_code:
                raise ValidationError(f"Category '{category.name}' has no short code configured in the master.")

            # Compute next sequential zero-padded asset ID under category lock
            last_asset = Asset.objects.filter(asset_id__startswith=f"{category_code}-").order_by("-id").first()
            if last_asset and "-" in last_asset.asset_id:
                try:
                    next_seq = int(last_asset.asset_id.split("-")[-1]) + 1
                except ValueError:
                    next_seq = Asset.objects.filter(category=category).count() + 1
            else:
                next_seq = Asset.objects.filter(category=category).count() + 1

            candidate_id = f"{category_code}-{next_seq:06d}"
            while Asset.objects.filter(asset_id=candidate_id).exists():
                next_seq += 1
                candidate_id = f"{category_code}-{next_seq:06d}"

            data["asset_id"] = candidate_id
            data["category_id"] = category.id

        # Serial number uniqueness validation
        sn = data.get("serial_number")
        if sn and str(sn).strip():
            sn = str(sn).strip()
            if Asset.objects.filter(serial_number=sn).exists():
                raise ValidationError(f"Serial number '{sn}' is already registered with another asset.")
            data["serial_number"] = sn
        else:
            data["serial_number"] = None

        user = getattr(context, "user", None)
        if user and user.is_authenticated:
            data["created_by_id"] = user.id

        data["asset_status"] = "Available"
        data["meta_status"] = "active"
        data["condition"] = data.get("condition") or "Good"
        data["status"] = data.get("status", 1)

        return data

    def before_update(self, context, instance, data):
        # Protect immutable identity
        data.pop("asset_id", None)
        data.pop("category", None)
        data.pop("category_id", None)
        data.pop("created_by", None)
        data.pop("created_by_id", None)
        data.pop("created_at", None)

        new_status = data.get("asset_status")
        if new_status and new_status != instance.asset_status:
            allowed = self.ALLOWED_TRANSITIONS.get(instance.asset_status, [])
            if new_status not in allowed and not getattr(context.user, "is_superadmin", False):
                raise ValidationError(f"Invalid asset status transition from '{instance.asset_status}' to '{new_status}'.")

        # Track condition changes
        new_condition = data.get("condition")
        if new_condition and new_condition != instance.condition:
            data["condition_last_assessed_at"] = timezone.now()
            user = getattr(context, "user", None)
            if user and user.is_authenticated:
                data["condition_last_assessed_by_id"] = user.id

        return data

    def after_create(self, context, instance):
        # Mandatory stock ledger write
        write_stock_ledger(
            asset=instance,
            transaction_type="IN",
            trigger_type="Purchase_Receipt",
            previous_state="",
            new_state="Available",
            performed_by=getattr(context, "user", None),
            reference_model="assets",
            reference_id=instance.id
        )
        return instance


# ============================================================================
# 4. ASSET PURCHASE SERVICE (PROCUREMENT & ROBUST GRN)
# ============================================================================

@register_service("asset_purchase")
class AssetPurchaseService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def _validate_items(self, items):
        if not items or not isinstance(items, list):
            raise ValidationError("Purchase must contain a non-empty list of items.")

        from .models import AssetCategory
        total_calculated = Decimal("0.00")

        for idx, item in enumerate(items):
            cat_id = item.get("category_id")
            if not cat_id or not AssetCategory.objects.filter(id=cat_id, is_active=True, status=1).exists():
                raise ValidationError(f"Item #{idx+1} references an invalid or inactive category ID ({cat_id}).")

            qty = item.get("quantity")
            if not isinstance(qty, int) or qty < 1:
                raise ValidationError(f"Item #{idx+1} quantity must be a positive integer.")

            price = item.get("unit_price")
            if price is None or Decimal(str(price)) < 0:
                raise ValidationError(f"Item #{idx+1} unit price cannot be negative.")

            tax = Decimal(str(item.get("tax_rate", 0)))
            line_total = Decimal(str(qty)) * Decimal(str(price)) * (Decimal("1.00") + (tax / Decimal("100.00")))
            total_calculated += line_total

        return round(total_calculated, 2)

    def before_create(self, context, data):
        from .models import AssetPurchase

        if "items" in data:
            data["total_amount"] = self._validate_items(data["items"])

        # Auto-sequence PO number: PO-1001, PO-1002...
        if not data.get("po_number"):
            last_po = AssetPurchase.objects.order_by("-id").first()
            next_po_num = (last_po.id + 1000) if last_po else 1001
            data["po_number"] = f"PO-{next_po_num}"

        user = getattr(context, "user", None)
        if user and user.is_authenticated:
            data["created_by_id"] = user.id

        data["purchase_status"] = data.get("purchase_status", "Draft")
        data["paid_amount"] = data.get("paid_amount", 0.00)

        # Financial payment status reconciliation
        paid = Decimal(str(data["paid_amount"]))
        total = Decimal(str(data.get("total_amount", 0.00)))
        if paid >= total and total > 0:
            data["payment_status"] = "Paid"
        elif paid > 0:
            data["payment_status"] = "Partially Paid"
        else:
            data["payment_status"] = "Unpaid"

        data["status"] = data.get("status", 1)
        return data

    def before_update(self, context, instance, data):
        # Save previous status for transition detection
        if not hasattr(context, "metadata"):
            context.metadata = {}
        context.metadata["prev_purchase_status"] = instance.purchase_status

        if "items" in data:
            data["total_amount"] = self._validate_items(data["items"])

        # Financial payment status reconciliation on update
        if "paid_amount" in data or "total_amount" in data:
            paid = Decimal(str(data.get("paid_amount", instance.paid_amount)))
            total = Decimal(str(data.get("total_amount", instance.total_amount)))
            if paid >= total and total > 0:
                data["payment_status"] = "Paid"
            elif paid > 0:
                data["payment_status"] = "Partially Paid"
            else:
                data["payment_status"] = "Unpaid"

        return data

    def after_update(self, context, instance):
        prev_status = getattr(context, "metadata", {}).get("prev_purchase_status")

        # TRANSITION-BASED GRN GOODS RECEIPT HOOK: Only fires when status transitions to "Received"
        if prev_status != "Received" and instance.purchase_status == "Received":
            from .models import Asset, AssetCategory

            with transaction.atomic():
                user = getattr(context, "user", None)
                updated_items = []

                for item in instance.items:
                    cat_id = item.get("category_id")
                    qty = int(item.get("quantity", 1))
                    received_qty = int(item.get("received_qty", 0))
                    remaining_qty = max(0, qty - received_qty)

                    if remaining_qty <= 0:
                        updated_items.append(item)
                        continue

                    # Concurrency-safe category sequence locking
                    category = AssetCategory.objects.select_for_update().get(id=cat_id)
                    category_code = category.code.strip().upper()

                    for _ in range(remaining_qty):
                        last_asset = Asset.objects.filter(asset_id__startswith=f"{category_code}-").order_by("-id").first()
                        next_seq = (int(last_asset.asset_id.split("-")[-1]) + 1) if (last_asset and "-" in last_asset.asset_id) else (Asset.objects.filter(category=category).count() + 1)
                        asset_id = f"{category_code}-{next_seq:06d}"
                        while Asset.objects.filter(asset_id=asset_id).exists():
                            next_seq += 1
                            asset_id = f"{category_code}-{next_seq:06d}"

                        new_asset = Asset.objects.create(
                            asset_id=asset_id,
                            category=category,
                            name=item.get("name", f"{category.name} Item"),
                            model=item.get("model", ""),
                            purchase=instance,
                            purchase_date=instance.purchase_date,
                            purchase_cost=item.get("unit_price"),
                            vendor_name=instance.vendor.name if instance.vendor else "",
                            asset_status="Available",
                            condition="Good",
                            created_by=user
                        )

                        write_stock_ledger(
                            asset=new_asset,
                            transaction_type="IN",
                            trigger_type="Purchase_Receipt",
                            previous_state="Ordered",
                            new_state="Available",
                            performed_by=user,
                            reference_model="assets_purchases",
                            reference_id=instance.id
                        )

                    item["received_qty"] = qty
                    updated_items.append(item)

                # Persist updated line-item received quantities
                instance.items = updated_items
                instance.save(update_fields=["items"])

        return instance


# ============================================================================
# 5. ASSET ALLOCATION SERVICE
# ============================================================================

@register_service("asset_allocation")
class AssetAllocationService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def before_create(self, context, data):
        from .models import Asset, AssetAllocation
        from django.contrib.auth import get_user_model
        User = get_user_model()

        asset_id = data.get("asset") or data.get("asset_id")
        employee_id = data.get("employee") or data.get("employee_id")

        if not asset_id or not employee_id:
            raise ValueError("Both asset and employee are required for allocation.")

        alloc_type = data.get("allocation_type", "Allocation")

        with transaction.atomic():
            # Concurrency protection: Lock asset row while evaluating allocation eligibility
            try:
                asset = Asset.objects.select_for_update().get(id=asset_id, status=1)
            except Asset.DoesNotExist:
                raise NotFoundError(f"Asset #{asset_id} not found.")

            try:
                employee = User.objects.get(id=employee_id, is_active=True)
            except User.DoesNotExist:
                raise NotFoundError(f"Active employee #{employee_id} not found.")

            # Transfer validation
            if alloc_type == "Transfer":
                if asset.asset_status != "Allocated":
                    raise ValidationError("Cannot request transfer: asset is not currently allocated.")
                
                transfer_from_id = data.get("transfer_from_employee") or data.get("transfer_from_employee_id") or asset.current_allocated_to_id
                if not transfer_from_id or transfer_from_id != asset.current_allocated_to_id:
                    raise ValidationError("Transfer source employee must match the asset's currently allocated assignee.")

                transfer_to_id = data.get("transfer_to_employee") or data.get("transfer_to_employee_id")
                if not transfer_to_id:
                    data["transfer_to_employee_id"] = employee.id
                    transfer_to_id = employee.id

                if str(transfer_from_id) == str(transfer_to_id):
                    raise ValidationError("Cannot transfer asset to the same employee who currently holds it.")

                data["transfer_from_employee_id"] = transfer_from_id
                data["transfer_to_employee_id"] = transfer_to_id

            else:
                # Standard Allocation: asset MUST be Available
                if asset.asset_status != "Available":
                    raise ValidationError(f"Asset '{asset.name}' is currently '{asset.asset_status}' and cannot be allocated.")

            # Duplicate pending request guard
            if AssetAllocation.objects.filter(asset=asset, allocation_status="Pending Approval", status=1).exists():
                raise ValidationError(f"Asset '{asset.name}' already has a pending allocation request.")

            # Atomically reserve asset for standard allocation
            if alloc_type != "Transfer":
                asset.asset_status = "Reserved"
                asset.save(update_fields=["asset_status"])

        user = getattr(context, "user", None)
        if user and user.is_authenticated:
            data["created_by_id"] = user.id

        data["allocation_status"] = "Pending Approval"
        data["status"] = data.get("status", 1)
        return data

    def before_update(self, context, instance, data):
        if not hasattr(context, "metadata"):
            context.metadata = {}
        context.metadata["prev_allocation_status"] = instance.allocation_status

        new_status = data.get("allocation_status")
        valid_transitions = {
            "Pending Approval": ["Active", "Rejected"],
            "Active": ["Returned", "Transferred"],
            "Returned": [],
            "Transferred": [],
            "Rejected": []
        }
        if new_status and new_status != instance.allocation_status:
            allowed = valid_transitions.get(instance.allocation_status, [])
            if new_status not in allowed and not getattr(context.user, "is_superadmin", False):
                raise ValidationError(f"Invalid allocation status transition from '{instance.allocation_status}' to '{new_status}'.")
        return data

    def after_update(self, context, instance):
        prev_status = getattr(context, "metadata", {}).get("prev_allocation_status")

        # TRANSITION GUARD: Only execute state changes and ledger writes when status actually changed!
        if prev_status == instance.allocation_status:
            return instance

        asset = instance.asset
        user = getattr(context, "user", None)

        with transaction.atomic():
            # 1. Allocation Approved -> Active
            if instance.allocation_status == "Active":
                prev_asset_state = asset.asset_status
                asset.asset_status = "Allocated"
                asset.current_allocated_to = instance.employee
                asset.current_allocation_id = instance.id
                asset.save(update_fields=["asset_status", "current_allocated_to", "current_allocation_id"])

                write_stock_ledger(
                    asset=asset,
                    transaction_type="OUT",
                    trigger_type="Employee_Allocation",
                    previous_state=prev_asset_state,
                    new_state="Allocated",
                    performed_by=user,
                    reference_model="assets_allocations",
                    reference_id=instance.id
                )

            # 2. Asset Returned
            elif instance.allocation_status == "Returned":
                prev_asset_state = asset.asset_status
                asset.asset_status = "Available"
                asset.current_allocated_to = None
                asset.current_allocation_id = None
                if instance.returned_condition:
                    asset.condition = instance.returned_condition
                    asset.condition_last_assessed_at = timezone.now()
                    asset.condition_last_assessed_by = user
                    asset.save(update_fields=["asset_status", "current_allocated_to", "current_allocation_id", "condition", "condition_last_assessed_at", "condition_last_assessed_by"])
                else:
                    asset.save(update_fields=["asset_status", "current_allocated_to", "current_allocation_id"])

                write_stock_ledger(
                    asset=asset,
                    transaction_type="IN",
                    trigger_type="Employee_Return",
                    previous_state=prev_asset_state,
                    new_state="Available",
                    performed_by=user,
                    reference_model="assets_allocations",
                    reference_id=instance.id
                )

            # 3. Asset Transferred
            elif instance.allocation_status == "Transferred" and instance.transfer_to_employee:
                prev_asset_state = asset.asset_status
                asset.current_allocated_to = instance.transfer_to_employee
                asset.save(update_fields=["current_allocated_to"])

                write_stock_ledger(
                    asset=asset,
                    transaction_type="OUT",
                    trigger_type="Employee_Allocation",
                    previous_state=prev_asset_state,
                    new_state="Allocated",
                    performed_by=user,
                    reference_model="assets_allocations",
                    reference_id=instance.id
                )

            # 4. Allocation Rejected -> Release Reservation
            elif instance.allocation_status == "Rejected" and asset.asset_status == "Reserved":
                asset.asset_status = "Available"
                asset.save(update_fields=["asset_status"])

        return instance


# ============================================================================
# 6. ASSET REPAIR SERVICE
# ============================================================================

@register_service("asset_repair")
class AssetRepairService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def before_create(self, context, data):
        from .models import Asset
        asset_id = data.get("asset") or data.get("asset_id")
        if not asset_id:
            raise ValueError("asset is required for repair checkout.")

        with transaction.atomic():
            try:
                asset = Asset.objects.select_for_update().get(id=asset_id, status=1)
            except Asset.DoesNotExist:
                raise NotFoundError(f"Asset #{asset_id} not found.")

            # Eligibility guard: cannot send already under repair, disposed, or lost assets
            if asset.asset_status in ("Under Repair", "Disposed", "Lost"):
                raise ValidationError(f"Cannot checkout asset for repair: asset is currently '{asset.asset_status}'.")

        user = getattr(context, "user", None)
        if user and user.is_authenticated:
            data["created_by_id"] = user.id

        data["repair_status"] = "Sent for Repair"
        data["status"] = data.get("status", 1)
        return data

    def after_create(self, context, instance):
        asset = instance.asset
        prev_status = asset.asset_status

        with transaction.atomic():
            asset.asset_status = "Under Repair"
            asset.save(update_fields=["asset_status"])

            write_stock_ledger(
                asset=asset,
                transaction_type="OUT",
                trigger_type="Send_To_Repair",
                previous_state=prev_status,
                new_state="Under Repair",
                performed_by=getattr(context, "user", None),
                reference_model="assets_repairs",
                reference_id=instance.id
            )
        return instance

    def before_update(self, context, instance, data):
        if not hasattr(context, "metadata"):
            context.metadata = {}
        context.metadata["prev_repair_status"] = instance.repair_status
        return data

    def after_update(self, context, instance):
        prev_status = getattr(context, "metadata", {}).get("prev_repair_status")

        # TRANSITION GUARD: Only execute on actual status change
        if prev_status == instance.repair_status:
            return instance

        asset = instance.asset
        user = getattr(context, "user", None)

        with transaction.atomic():
            if instance.repair_status == "Repaired":
                prev_asset_state = asset.asset_status
                asset.asset_status = "Available"
                asset.condition = instance.repair_condition or "Good"
                asset.condition_last_assessed_at = timezone.now()
                asset.condition_last_assessed_by = user
                asset.save(update_fields=["asset_status", "condition", "condition_last_assessed_at", "condition_last_assessed_by"])

                write_stock_ledger(
                    asset=asset,
                    transaction_type="IN",
                    trigger_type="Repair_Return",
                    previous_state=prev_asset_state,
                    new_state="Available",
                    performed_by=user,
                    reference_model="assets_repairs",
                    reference_id=instance.id
                )

            elif instance.repair_status == "Beyond Repair":
                prev_asset_state = asset.asset_status
                asset.asset_status = "Disposed"
                asset.save(update_fields=["asset_status"])

                write_stock_ledger(
                    asset=asset,
                    transaction_type="OUT",
                    trigger_type="Write_Off_Disposal",
                    previous_state=prev_asset_state,
                    new_state="Disposed",
                    performed_by=user,
                    reference_model="assets_repairs",
                    reference_id=instance.id
                )

        return instance


# ============================================================================
# 7. ASSET INCIDENT SERVICE
# ============================================================================

@register_service("asset_incident")
class AssetIncidentService(BaseService):
    def check_permission(self, context):
        user = getattr(context, "user", None)
        if getattr(user, "is_superadmin", False):
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return None

    def before_create(self, context, data):
        from .models import Asset, AssetAllocation
        asset_id = data.get("asset") or data.get("asset_id")
        if not asset_id:
            raise ValueError("asset is required for incident report.")

        try:
            asset = Asset.objects.get(id=asset_id, status=1)
        except Asset.DoesNotExist:
            raise NotFoundError(f"Asset #{asset_id} not found.")

        user = getattr(context, "user", None)
        if not user or not user.is_authenticated:
            raise AuthorizationError("Authentication required to report an asset incident.")

        # Non-superadmin cannot report an incident on behalf of another employee
        if not getattr(user, "is_superadmin", False):
            req_emp = data.get("employee") or data.get("employee_id")
            if req_emp and str(req_emp) != str(user.id):
                raise AuthorizationError("Cannot report an incident on behalf of another employee.")
            data["employee_id"] = user.id
        else:
            if not data.get("employee") and not data.get("employee_id"):
                data["employee_id"] = user.id

        data["created_by_id"] = user.id

        # Validate allocation relation if provided
        alloc_id = data.get("allocation") or data.get("allocation_id")
        if alloc_id:
            try:
                allocation = AssetAllocation.objects.get(id=alloc_id, asset=asset)
                data["allocation_id"] = allocation.id
            except AssetAllocation.DoesNotExist:
                raise ValidationError(f"Allocation #{alloc_id} does not match asset #{asset_id}.")

        data["incident_status"] = "Reported"
        data["status"] = data.get("status", 1)
        return data

    def after_create(self, context, instance):
        # Accurate stock ledger and asset state recording
        if instance.incident_type in ("Loss", "Theft"):
            asset = instance.asset
            prev_status = asset.asset_status

            with transaction.atomic():
                asset.asset_status = "Lost"
                asset.save(update_fields=["asset_status"])

                write_stock_ledger(
                    asset=asset,
                    transaction_type="OUT",
                    trigger_type="Incident_Loss",
                    previous_state=prev_status,
                    new_state="Lost",
                    performed_by=getattr(context, "user", None),
                    reference_model="assets_incidents",
                    reference_id=instance.id
                )
        return instance


# ============================================================================
# 9. ASSET INVOICE SERVICE
# ============================================================================

@register_service("asset_invoice")
class AssetInvoiceService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return models.Q(lifecycle_status=1)

    def before_create(self, context, data):
        purchase_id = data.get("purchase") or data.get("purchase_id") or data.get("purchaseId")
        if not purchase_id:
            raise ValueError("purchase is required for asset invoice.")
        data["purchase_id"] = purchase_id if not hasattr(purchase_id, "id") else purchase_id.id

        if not data.get("invoice_number"):
            raise ValueError("invoice_number is required.")
        if not data.get("invoice_date"):
            raise ValueError("invoice_date is required.")
        if not data.get("due_date"):
            raise ValueError("due_date is required.")

        sub_total = Decimal(str(data.get("sub_total") or data.get("subTotal") or 0))
        tax_amount = Decimal(str(data.get("tax_amount") or data.get("taxAmount") or 0))
        total_amount = sub_total + tax_amount

        data["sub_total"] = round(sub_total, 2)
        data["tax_amount"] = round(tax_amount, 2)
        data["total_amount"] = round(total_amount, 2)
        data["status"] = data.get("status", "Pending")
        data["meta_status"] = "active"
        data["lifecycle_status"] = 1
        return data


# ============================================================================
# 10. ASSET PAYMENT SERVICE
# ============================================================================

@register_service("asset_payment")
class AssetPaymentService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return models.Q(lifecycle_status=1)

    def before_create(self, context, data):
        invoice_id = data.get("invoice") or data.get("invoice_id") or data.get("invoiceId")
        if not invoice_id:
            raise ValueError("invoice is required for asset payment.")
        data["invoice_id"] = invoice_id if not hasattr(invoice_id, "id") else invoice_id.id

        amt = Decimal(str(data.get("amount_paid") or data.get("amountPaid") or 0))
        if amt <= Decimal('0.00'):
            raise ValueError("amount_paid must be greater than zero.")

        data["amount_paid"] = round(amt, 2)
        data["payment_date"] = data.get("payment_date") or data.get("paymentDate") or timezone.now().date()
        data["status"] = data.get("status", "Success")
        data["lifecycle_status"] = 1
        return data

    def after_create(self, context, instance):
        if instance.status == "Success":
            inv = instance.invoice
            from .models import AssetPayment
            total_paid = AssetPayment.objects.filter(
                invoice=inv,
                status="Success",
                lifecycle_status=1
            ).aggregate(tot=models.Sum("amount_paid"))["tot"] or Decimal('0.00')

            if total_paid >= inv.total_amount:
                inv.status = "Paid"
                inv.save(update_fields=["status", "updated_at"])
        return instance
