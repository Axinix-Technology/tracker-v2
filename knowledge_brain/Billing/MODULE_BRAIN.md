# Module Brain: Billing & Client Invoicing

> **Domain:** Client Invoicing, Quotations, Order Acknowledgements, Payments, and Double-Entry Client Ledgers.  
> **App Location:** `backend_django/billing/`  
> **Tables:** `billing_quotations`, `billing_quotation_revisions`, `billing_order_acknowledgements`, `billing_invoices`, `billing_payments`, `billing_payment_journals`, `billing_client_ledgers`, `billing_period_closures`.  
> **Asset Purchases:** `assets_invoices`, `assets_payments` (under `backend_django/assets/`).

---

## 1. Domain Overview & Architectural Principles

The Billing suite manages the full Quote-to-Cash (Q2C) enterprise lifecycle:
1. **Quotation (`Quotation`)**: Client quotes with structured line items, deterministic tax/discount computation, and sequential numbering (`QUO-YYYY-XXXX`).
2. **Quotation Revision (`QuotationRevision`)**: Immutable historical snapshots capturing prior quote states whenever revisions are requested.
3. **Order Acknowledgement (`OrderAcknowledgement`)**: Legally binding customer contracts signed off internally and externally.
4. **Invoice (`Invoice`)**: Accounts Receivable invoices generated against orders or milestones with automatic aging and status syncing (`Draft` &rarr; `Issued` &rarr; `Partially Paid` &rarr; `Paid`).
5. **Payment (`Payment`)**: Direct customer payments reconciling against outstanding invoice balances.
6. **Payment Journal (`PaymentJournal`)**: Bank verification receipt vouchers with financial audit attachments.
7. **Client Ledger (`ClientLedger`)**: Immutable append-only double-entry financial ledger recording debits (invoices) and credits (payments) with continuous running balance tracking.
8. **Period Closure (`PeriodClosure`)**: Financial period locks preventing backdated mutations across closed billing, payroll, and expense cycles.

---

## 2. Models & Schema Declarations

| Model | Table | Type | Direct Mutations | Key Fields |
|---|---|---|---|---|
| `Quotation` | `billing_quotations` | Transaction | Standard | `quotation_number`, `client`, `line_items`, `subtotal`, `grand_total`, `status` |
| `QuotationRevision` | `billing_quotation_revisions` | Snapshot Ledger | Append-Only (`allow_direct_update=False`) | `quotation`, `revision_number`, `snapshot`, `changed_by` |
| `OrderAcknowledgement` | `billing_order_acknowledgements` | Contract | Standard | `order_number`, `quotation`, `client`, `modules`, `total_order_value`, `status` |
| `Invoice` | `billing_invoices` | Transaction | Standard | `invoice_number`, `client`, `contract`, `line_items`, `total_amount`, `balance_due`, `status` |
| `Payment` | `billing_payments` | Transaction | Standard | `client`, `invoice`, `oa`, `amount`, `payment_date`, `status` |
| `PaymentJournal` | `billing_payment_journals` | Voucher | Standard | `receipt_number`, `client`, `order`, `amount`, `bank_name`, `status` |
| `ClientLedger` | `billing_client_ledgers` | Audit Ledger | Append-Only (`allow_direct_update=False`) | `client`, `date`, `type` (Credit/Debit), `amount`, `running_balance`, `reference_model`, `reference_id` |
| `PeriodClosure` | `billing_period_closures` | Governance Lock | Standard | `period_label`, `start_date`, `end_date`, `status`, `modules` |

---

## 3. Services & Hook Lifecycles

### QuotationService (`@register_service("quotation")`)
- **`before_create`**: Generates sequential `QUO-YYYY-XXXX`. Runs deterministic line-item math (`subtotal`, `discount`, `tax`, `grand_total`).
- **`before_update`**: Recalculates figures upon line item edits. When transitioning to `Revision Requested`, triggers immutable snapshot creation in `QuotationRevision`.

### InvoiceService (`@register_service("invoice")`)
- **`before_create`**: Generates sequential `INV-YYYY-XXXX`. Initializes `paid_amount = 0.00` and `balance_due = total_amount`.
- **`before_update`**: Freezes financial figures once invoice is `Paid` or `Cancelled`. Auto-calculates `balance_due` and synchronizes status (`Partially Paid`, `Paid`).
- **`after_update`**: On transition to `Issued`, asynchronously posts a `Debit` entry to `ClientLedger` within `transaction.on_commit(...)`.

### PaymentService (`@register_service("payment")`)
- **`before_create`**: Validates payment amount `> 0`.
- **`after_create`**: Atomically reconciles against linked `Invoice` (updating `paid_amount` and `balance_due`) and posts a `Credit` entry to `ClientLedger` within `transaction.on_commit(...)`.

### ClientLedgerService (`@register_service("client_ledger")`)
- **Immutability Guard**: Blocks direct user mutations. Entries are generated programmatically via verified financial transactions.

### PeriodClosureService (`@register_service("period_closure")`)
- **Overlap Guard**: Validates `start_date <= end_date` and blocks overlapping active closures.

