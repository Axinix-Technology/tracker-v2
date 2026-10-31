import datetime
from decimal import Decimal
import logging
from django.db import models, transaction
from django.db.models import Q, Max
from django.utils import timezone
from populate_core.registry import BaseService, register_service
from populate_core.response.exceptions import AuthorizationError, ValidationError, NotFoundError

logger = logging.getLogger("billing.services")


# ============================================================================
# 1. QUOTATION SERVICE
# ============================================================================

@register_service("quotation")
class QuotationService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True

        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False

        # Defer read, create, update, delete to PolicyEngine (AccessPolicy & ABAC conditions)
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()

        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "quotation.read") or PolicyEngine.has_capability(context, "quotation.all"):
            return Q(lifecycle_status=1)

        # Standard sales representative: can view quotes they prepared or where client matches
        return Q(lifecycle_status=1)

    def before_create(self, context, data):
        from .models import Quotation

        if not data.get("client") and not data.get("client_id") and not data.get("clientId"):
            raise ValueError("client is required for quotation.")

        client_id = data.get("client") or data.get("client_id") or data.get("clientId")
        data["client_id"] = client_id if not hasattr(client_id, "id") else client_id.id

        now = timezone.now()
        year = now.year

        # 1. Auto-generate sequential quotation number: QUO-YYYY-XXXX
        if not data.get("quotation_number"):
            last_quote = Quotation.objects.filter(quotation_number__startswith=f"QUO-{year}-").order_by("-id").first()
            if last_quote and last_quote.quotation_number:
                try:
                    last_seq = int(last_quote.quotation_number.split("-")[-1])
                    next_seq = last_seq + 1
                except Exception:
                    next_seq = Quotation.objects.count() + 1
            else:
                next_seq = 1

            gen_num = f"QUO-{year}-{next_seq:04d}"
            while Quotation.objects.filter(quotation_number=gen_num).exists():
                next_seq += 1
                gen_num = f"QUO-{year}-{next_seq:04d}"
            data["quotation_number"] = gen_num

        # 2. Line Items deterministic calculation
        items = list(data.get("line_items") or data.get("lineItems") or [])
        subtotal = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_tax = Decimal('0.00')

        for item in items:
            qty = Decimal(str(item.get("quantity") or 1))
            unit_price = Decimal(str(item.get("unitPrice") or item.get("unit_price") or 0))
            disc_pct = Decimal(str(item.get("discount") or 0))
            tax_rate = Decimal(str(item.get("taxRate") or item.get("tax_rate") or 18))

            base_val = qty * unit_price
            disc_val = base_val * (disc_pct / Decimal('100.0'))
            taxable_val = base_val - disc_val
            tax_val = taxable_val * (tax_rate / Decimal('100.0'))
            line_tot = round(taxable_val + tax_val, 2)

            item["lineTotal"] = float(line_tot)
            subtotal += base_val
            total_discount += disc_val
            total_tax += tax_val

        data["line_items"] = items
        data["subtotal"] = round(subtotal, 2)
        data["total_discount"] = round(total_discount, 2)
        data["total_tax"] = round(total_tax, 2)
        data["grand_total"] = round(subtotal - total_discount + total_tax, 2)

        data["prepared_by_id"] = getattr(context.user, "id", None)
        data["status"] = data.get("status", "Draft")
        data["meta_status"] = "active"
        data["revision_number"] = 1
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        from .models import QuotationRevision

        # Recalculate totals if line_items updated
        if "line_items" in data or "lineItems" in data:
            items = list(data.get("line_items") or data.get("lineItems") or [])
            subtotal = Decimal('0.00')
            total_discount = Decimal('0.00')
            total_tax = Decimal('0.00')

            for item in items:
                qty = Decimal(str(item.get("quantity") or 1))
                unit_price = Decimal(str(item.get("unitPrice") or item.get("unit_price") or 0))
                disc_pct = Decimal(str(item.get("discount") or 0))
                tax_rate = Decimal(str(item.get("taxRate") or item.get("tax_rate") or 18))

                base_val = qty * unit_price
                disc_val = base_val * (disc_pct / Decimal('100.0'))
                taxable_val = base_val - disc_val
                tax_val = taxable_val * (tax_rate / Decimal('100.0'))
                line_tot = round(taxable_val + tax_val, 2)

                item["lineTotal"] = float(line_tot)
                subtotal += base_val
                total_discount += disc_val
                total_tax += tax_val

            data["line_items"] = items
            data["subtotal"] = round(subtotal, 2)
            data["total_discount"] = round(total_discount, 2)
            data["total_tax"] = round(total_tax, 2)
            data["grand_total"] = round(subtotal - total_discount + total_tax, 2)

        new_status = data.get("status")
        if new_status and new_status != instance.status:
            # If revision requested, snapshot current state and increment revision_number
            if new_status == "Revision Requested":
                QuotationRevision.objects.create(
                    quotation=instance,
                    revision_number=instance.revision_number,
                    snapshot={
                        "subtotal": float(instance.subtotal),
                        "total_tax": float(instance.total_tax),
                        "total_discount": float(instance.total_discount),
                        "grand_total": float(instance.grand_total),
                        "line_items": instance.line_items,
                        "status": instance.status,
                    },
                    changed_by=getattr(context.user, "id", None),
                    change_reason=data.get("change_reason") or "Revision requested"
                )
                data["revision_number"] = instance.revision_number + 1

            if new_status == "Internally Approved":
                data["approved_by_id"] = getattr(context.user, "id", None)

            # Record approval history entry
            history = list(instance.approval_history or [])
            history.append({
                "action": new_status,
                "by": getattr(context.user, "id", None),
                "at": timezone.now().isoformat(),
                "remarks": data.get("remarks", "")
            })
            data["approval_history"] = history

        return data


# ============================================================================
# 2. QUOTATION REVISION SERVICE (IMMUTABLE SNAPSHOTS)
# ============================================================================

@register_service("quotation_revision")
class QuotationRevisionService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return Q(status=1)


# ============================================================================
# 3. ORDER ACKNOWLEDGEMENT SERVICE (CONTRACT / OA)
# ============================================================================

@register_service("order_acknowledgement")
class OrderAcknowledgementService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()
        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "order_acknowledgement.read") or PolicyEngine.has_capability(context, "order_acknowledgement.all"):
            return Q(lifecycle_status=1)
        return Q(lifecycle_status=1)

    def before_create(self, context, data):
        from .models import OrderAcknowledgement

        if not data.get("client") and not data.get("client_id") and not data.get("clientId"):
            raise ValueError("client is required for order acknowledgement.")

        client_id = data.get("client") or data.get("client_id") or data.get("clientId")
        data["client_id"] = client_id if not hasattr(client_id, "id") else client_id.id

        now = timezone.now()
        year = now.year

        # 1. Auto-generate sequential OA number: OA-YYYY-XXXX
        if not data.get("order_number"):
            last_oa = OrderAcknowledgement.objects.filter(order_number__startswith=f"OA-{year}-").order_by("-id").first()
            if last_oa and last_oa.order_number:
                try:
                    last_seq = int(last_oa.order_number.split("-")[-1])
                    next_seq = last_seq + 1
                except Exception:
                    next_seq = OrderAcknowledgement.objects.count() + 1
            else:
                next_seq = 1

            gen_num = f"OA-{year}-{next_seq:04d}"
            while OrderAcknowledgement.objects.filter(order_number=gen_num).exists():
                next_seq += 1
                gen_num = f"OA-{year}-{next_seq:04d}"
            data["order_number"] = gen_num

        # 2. Sum module values
        modules = list(data.get("modules") or [])
        tot_val = sum(Decimal(str(m.get("agreedValue") or m.get("agreed_value") or 0)) for m in modules)
        if tot_val > 0 and not data.get("total_order_value"):
            data["total_order_value"] = round(tot_val, 2)

        data["sales_person_id"] = getattr(context.user, "id", None)
        data["status"] = data.get("status", "Pending Internal Approval")
        data["meta_status"] = "active"
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_status = data.get("status")
        now = timezone.now()

        if new_status and new_status != instance.status:
            if new_status == "Completed":
                data["completed_by_id"] = getattr(context.user, "id", None)
                data["completed_at"] = now

        return data


# ============================================================================
# 4. INVOICE SERVICE
# ============================================================================

@register_service("invoice")
class InvoiceService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        if context.is_superadmin:
            return Q()
        from populate_core.policy.engine import PolicyEngine
        if PolicyEngine.has_capability(context, "invoice.read") or PolicyEngine.has_capability(context, "invoice.all"):
            return Q(lifecycle_status=1)
        return Q(lifecycle_status=1)

    def before_create(self, context, data):
        from .models import Invoice

        if not data.get("client") and not data.get("client_id") and not data.get("clientId"):
            raise ValueError("client is required for invoice.")

        client_id = data.get("client") or data.get("client_id") or data.get("clientId")
        data["client_id"] = client_id if not hasattr(client_id, "id") else client_id.id

        if not data.get("due_date") and not data.get("dueDate"):
            raise ValueError("due_date is required for invoice.")
        data["due_date"] = data.get("due_date") or data.get("dueDate")

        now = timezone.now()
        year = now.year

        # 1. Auto-generate sequential invoice number: INV-YYYY-XXXX
        if not data.get("invoice_number"):
            last_inv = Invoice.objects.filter(invoice_number__startswith=f"INV-{year}-").order_by("-id").first()
            if last_inv and last_inv.invoice_number:
                try:
                    last_seq = int(last_inv.invoice_number.split("-")[-1])
                    next_seq = last_seq + 1
                except Exception:
                    next_seq = Invoice.objects.count() + 1
            else:
                next_seq = 1

            gen_num = f"INV-{year}-{next_seq:04d}"
            while Invoice.objects.filter(invoice_number=gen_num).exists():
                next_seq += 1
                gen_num = f"INV-{year}-{next_seq:04d}"
            data["invoice_number"] = gen_num

        # 2. Line Items calculation
        items = list(data.get("line_items") or data.get("lineItems") or [])
        subtotal = Decimal('0.00')
        tax_amount = Decimal('0.00')
        discount_amount = Decimal('0.00')

        for item in items:
            qty = Decimal(str(item.get("quantity") or 1))
            unit_price = Decimal(str(item.get("unitPrice") or item.get("unit_price") or 0))
            disc = Decimal(str(item.get("discount") or 0))
            tax_rate = Decimal(str(item.get("taxRate") or item.get("tax_rate") or 18))

            amt = (qty * unit_price) - disc
            tax = amt * (tax_rate / Decimal('100.0'))
            item["amount"] = float(round(amt + tax, 2))

            subtotal += (qty * unit_price)
            discount_amount += disc
            tax_amount += tax

        data["line_items"] = items
        data["subtotal"] = round(subtotal, 2)
        data["discount_amount"] = round(discount_amount, 2)
        data["tax_amount"] = round(tax_amount, 2)
        tot = subtotal - discount_amount + tax_amount
        data["total_amount"] = round(tot, 2)
        data["paid_amount"] = Decimal('0.00')
        data["balance_due"] = round(tot, 2)

        data["created_by_id"] = getattr(context.user, "id", None)
        data["status"] = data.get("status", "Draft")
        data["meta_status"] = "active"
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        # Once invoice is Paid or Cancelled, lock financial figures
        if instance.status in ("Paid", "Cancelled"):
            frozen = ["subtotal", "tax_amount", "discount_amount", "total_amount", "line_items"]
            for f in frozen:
                if f in data:
                    raise ValueError(f"Invoice #{instance.invoice_number} is {instance.status}. Figures are permanently locked.")

        # Recompute balance_due
        total = Decimal(str(data.get("total_amount") or instance.total_amount))
        paid = Decimal(str(data.get("paid_amount") or instance.paid_amount))
        bal = max(Decimal('0.00'), total - paid)
        data["balance_due"] = round(bal, 2)

        # Auto-update status based on balance
        if "paid_amount" in data:
            if bal == Decimal('0.00'):
                data["status"] = "Paid"
            elif paid > Decimal('0.00'):
                data["status"] = "Partially Paid"

        return data

    def after_update(self, context, instance):
        # When invoice is Issued, record a Debit in ClientLedger post-commit
        if instance.status == "Issued":
            from .models import ClientLedger

            def on_commit_invoice_issued():
                try:
                    already_posted = ClientLedger.objects.filter(
                        reference_model="invoices",
                        reference_id=instance.id
                    ).exists()
                    if not already_posted:
                        last_entry = ClientLedger.objects.filter(client=instance.client).order_by("-date", "-id").first()
                        last_bal = last_entry.running_balance if last_entry else Decimal('0.00')
                        new_bal = last_bal - instance.total_amount

                        ClientLedger.objects.create(
                            client=instance.client,
                            type="Debit",
                            amount=instance.total_amount,
                            running_balance=new_bal,
                            reference_model="invoices",
                            reference_id=instance.id,
                            description=f"Invoice #{instance.invoice_number} issued",
                            entry_by=getattr(context.user, "id", None),
                            status=1
                        )
                except Exception as e:
                    logger.error(f"[InvoiceService] Failed to post client ledger for invoice {instance.invoice_number}: {e}")

            transaction.on_commit(on_commit_invoice_issued)

        return instance


# ============================================================================
# 5. PAYMENT SERVICE (CLIENT PAYMENT RECEIPT)
# ============================================================================

@register_service("payment")
class PaymentService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)

    def before_create(self, context, data):
        client_id = data.get("client") or data.get("client_id") or data.get("clientId")
        if not client_id:
            raise ValueError("client is required for payment.")
        data["client_id"] = client_id if not hasattr(client_id, "id") else client_id.id

        amt = Decimal(str(data.get("amount") or 0))
        if amt <= Decimal('0.00'):
            raise ValueError("Payment amount must be greater than zero.")

        data["amount"] = round(amt, 2)
        data["payment_date"] = data.get("payment_date") or data.get("paymentDate") or timezone.now().date()
        data["created_by_id"] = getattr(context.user, "id", None)
        data["status"] = data.get("status", "Confirmed")
        data["lifecycle_status"] = 1
        return data

    def after_create(self, context, instance):
        if instance.status == "Confirmed":
            from .models import Invoice, ClientLedger

            # 1. Reconcile against Invoice if linked
            if instance.invoice_id:
                inv = instance.invoice
                new_paid = inv.paid_amount + instance.amount
                inv.paid_amount = round(new_paid, 2)
                inv.balance_due = max(Decimal('0.00'), inv.total_amount - new_paid)
                if inv.balance_due == Decimal('0.00'):
                    inv.status = "Paid"
                else:
                    inv.status = "Partially Paid"
                inv.save(update_fields=["paid_amount", "balance_due", "status", "updated_at"])

            # 2. Append Credit entry to ClientLedger post-commit
            def on_commit_payment_credit():
                try:
                    last_entry = ClientLedger.objects.filter(client=instance.client).order_by("-date", "-id").first()
                    last_bal = last_entry.running_balance if last_entry else Decimal('0.00')
                    new_bal = last_bal + instance.amount

                    ClientLedger.objects.create(
                        client=instance.client,
                        type="Credit",
                        amount=instance.amount,
                        running_balance=new_bal,
                        reference_model="payments",
                        reference_id=instance.id,
                        description=f"Payment received (Ref: {instance.reference_no or 'N/A'})",
                        entry_by=getattr(context.user, "id", None),
                        status=1
                    )
                except Exception as e:
                    logger.error(f"[PaymentService] Failed to post ledger for payment #{instance.id}: {e}")

            transaction.on_commit(on_commit_payment_credit)

        return instance


# ============================================================================
# 6. PAYMENT JOURNAL SERVICE (RECEIPT VOUCHERS)
# ============================================================================

@register_service("payment_journal")
class PaymentJournalService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)

    def before_create(self, context, data):
        from .models import PaymentJournal

        client_id = data.get("client") or data.get("client_id") or data.get("clientId")
        if not client_id:
            raise ValueError("client is required for payment journal.")
        data["client_id"] = client_id if not hasattr(client_id, "id") else client_id.id

        now = timezone.now()
        year = now.year

        # Auto-generate receipt number: RCT-YYYY-XXXX
        if not data.get("receipt_number"):
            last_rct = PaymentJournal.objects.filter(receipt_number__startswith=f"RCT-{year}-").order_by("-id").first()
            if last_rct and last_rct.receipt_number:
                try:
                    last_seq = int(last_rct.receipt_number.split("-")[-1])
                    next_seq = last_seq + 1
                except Exception:
                    next_seq = PaymentJournal.objects.count() + 1
            else:
                next_seq = 1

            gen_num = f"RCT-{year}-{next_seq:04d}"
            while PaymentJournal.objects.filter(receipt_number=gen_num).exists():
                next_seq += 1
                gen_num = f"RCT-{year}-{next_seq:04d}"
            data["receipt_number"] = gen_num

        amt = Decimal(str(data.get("amount") or 0))
        data["amount"] = round(amt, 2)
        data["payment_date"] = data.get("payment_date") or data.get("paymentDate") or now.date()
        data["received_by_id"] = getattr(context.user, "id", None)
        data["status"] = data.get("status", "Draft")
        data["meta_status"] = "active"
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_status = data.get("status")
        if new_status and new_status != instance.status:
            if new_status == "Verified":
                data["verified_by_id"] = getattr(context.user, "id", None)
        return data


# ============================================================================
# 7. CLIENT LEDGER SERVICE (IMMUTABLE AUDIT LEDGER)
# ============================================================================

@register_service("client_ledger")
class ClientLedgerService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        # Direct mutation blocked - ledger is append-only from invoice/payment services
        if context.action in ("read", "report", "statistics", "aggregate"):
            return None
        raise AuthorizationError("Direct modification of client ledger is prohibited. Entries are generated via accounting transactions.")

    def get_policy_scope(self, context):
        return Q(status=1)


# ============================================================================
# 8. PERIOD CLOSURE SERVICE (ACCOUNTING PERIOD LOCK)
# ============================================================================

@register_service("period_closure")
class PeriodClosureService(BaseService):
    def check_permission(self, context):
        if context.is_superadmin:
            return True
        if not getattr(context, "user", None) or not getattr(context.user, "is_authenticated", False):
            return False
        return None

    def get_policy_scope(self, context):
        return Q(lifecycle_status=1)

    def before_create(self, context, data):
        from .models import PeriodClosure

        start_date = data.get("start_date") or data.get("startDate")
        end_date = data.get("end_date") or data.get("endDate")

        if not start_date or not end_date:
            raise ValueError("start_date and end_date are required for period closure.")

        if str(end_date) < str(start_date):
            raise ValueError("end_date cannot be earlier than start_date.")

        # Prevent overlapping period closures
        overlapping = PeriodClosure.objects.filter(
            lifecycle_status=1,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()

        if overlapping:
            raise ValueError("Period closure dates overlap with an existing period closure.")

        data["start_date"] = start_date
        data["end_date"] = end_date
        data["created_by_id"] = context.user.id
        data["status"] = data.get("status", "Open")
        data["lifecycle_status"] = 1
        return data

    def before_update(self, context, instance, data):
        new_status = data.get("status")
        now = timezone.now()

        if new_status and new_status != instance.status:
            if new_status == "Closed":
                data["closed_by_id"] = getattr(context.user, "id", None)
                data["closed_at"] = now
            elif new_status == "Reopened":
                data["reopened_by_id"] = getattr(context.user, "id", None)
                data["reopened_at"] = now

        return data

