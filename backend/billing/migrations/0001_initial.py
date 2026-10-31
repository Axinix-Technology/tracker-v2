import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0002_basicinfo_professionalinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quotation_number', models.CharField(blank=True, db_index=True, max_length=64, null=True, unique=True)),
                ('opportunity_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('contact_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('line_items', models.JSONField(default=list, help_text='List of line items')),
                ('subtotal', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('total_tax', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('total_discount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('grand_total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('valid_until', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('terms_and_conditions', models.TextField(blank=True, null=True)),
                ('status', models.CharField(db_index=True, default='Draft', max_length=64)),
                ('meta_status', models.CharField(db_index=True, default='active', max_length=32)),
                ('lifecycle_status', models.IntegerField(db_index=True, default=1)),
                ('revision_number', models.IntegerField(default=1)),
                ('approval_history', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_quotations', to=settings.AUTH_USER_MODEL)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotations', to='users.client')),
                ('parent_quotation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_quotations', to='billing.quotation')),
                ('prepared_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prepared_quotations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'billing_quotations',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='QuotationRevision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('revision_number', models.IntegerField()),
                ('snapshot', models.JSONField(help_text='Immutable state snapshot of quotation at time of revision')),
                ('change_reason', models.TextField(blank=True, null=True)),
                ('status', models.IntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quotation_revisions', to=settings.AUTH_USER_MODEL)),
                ('quotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revisions', to='billing.quotation')),
            ],
            options={
                'db_table': 'billing_quotation_revisions',
                'ordering': ['quotation', '-revision_number'],
            },
        ),
        migrations.CreateModel(
            name='OrderAcknowledgement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(blank=True, db_index=True, max_length=64, null=True, unique=True)),
                ('opportunity_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('modules', models.JSONField(default=list)),
                ('total_order_value', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('client_approval', models.JSONField(default=dict)),
                ('internal_approval', models.JSONField(default=dict)),
                ('status', models.CharField(db_index=True, default='Pending Internal Approval', max_length=64)),
                ('meta_status', models.CharField(db_index=True, default='active', max_length=32)),
                ('lifecycle_status', models.IntegerField(db_index=True, default=1)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('expected_end_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_acknowledgements', to='users.client')),
                ('completed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='completed_orders', to=settings.AUTH_USER_MODEL)),
                ('quotation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_acknowledgements', to='billing.quotation')),
                ('sales_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'billing_order_acknowledgements',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(db_index=True, max_length=64, unique=True)),
                ('opportunity_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('issue_date', models.DateField(db_index=True, default=django.utils.timezone.now)),
                ('due_date', models.DateField(db_index=True)),
                ('currency', models.CharField(default='INR', max_length=16)),
                ('line_items', models.JSONField(default=list)),
                ('subtotal', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('total_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('balance_due', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14)),
                ('status', models.CharField(db_index=True, default='Draft', max_length=32)),
                ('payment_milestone_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('gstin', models.CharField(blank=True, max_length=64, null=True)),
                ('billing_address', models.JSONField(default=dict)),
                ('notes', models.TextField(blank=True, null=True)),
                ('terms', models.TextField(blank=True, null=True)),
                ('meta_status', models.CharField(db_index=True, default='active', max_length=32)),
                ('lifecycle_status', models.IntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='users.client')),
                ('contract', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to='billing.orderacknowledgement')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_invoices', to=settings.AUTH_USER_MODEL)),
                ('quotation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to='billing.quotation')),
            ],
            options={
                'db_table': 'billing_invoices',
                'ordering': ['-issue_date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('payment_date', models.DateField(db_index=True, default=django.utils.timezone.now)),
                ('payment_method', models.CharField(default='Bank Transfer', max_length=64)),
                ('reference_no', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('status', models.CharField(db_index=True, default='Confirmed', max_length=32)),
                ('notes', models.TextField(blank=True, null=True)),
                ('attachments', models.JSONField(default=list)),
                ('lifecycle_status', models.IntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='users.client')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_payments', to=settings.AUTH_USER_MODEL)),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='billing.invoice')),
                ('oa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='billing.orderacknowledgement')),
            ],
            options={
                'db_table': 'billing_payments',
                'ordering': ['-payment_date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='PaymentJournal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_number', models.CharField(db_index=True, max_length=64, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('payment_date', models.DateField(db_index=True, default=django.utils.timezone.now)),
                ('payment_mode', models.CharField(default='Bank Transfer', max_length=64)),
                ('reference_number', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('bank_name', models.CharField(blank=True, max_length=128, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('attachments', models.JSONField(default=list)),
                ('status', models.CharField(db_index=True, default='Draft', max_length=32)),
                ('meta_status', models.CharField(db_index=True, default='active', max_length=32)),
                ('lifecycle_status', models.IntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_journals', to='users.client')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_journals', to='billing.orderacknowledgement')),
                ('received_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_journals', to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_journals', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'billing_payment_journals',
                'ordering': ['-payment_date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='PeriodClosure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_label', models.CharField(max_length=128)),
                ('start_date', models.DateField(db_index=True)),
                ('end_date', models.DateField(db_index=True)),
                ('financial_year_label', models.CharField(db_index=True, max_length=64)),
                ('status', models.CharField(db_index=True, default='Open', max_length=32)),
                ('modules', models.JSONField(default=dict)),
                ('summary', models.JSONField(default=dict)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('closure_remarks', models.TextField(blank=True, null=True)),
                ('reopened_at', models.DateTimeField(blank=True, null=True)),
                ('reopen_reason', models.TextField(blank=True, null=True)),
                ('lifecycle_status', models.IntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('closed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='finalized_period_closures', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_period_closures', to=settings.AUTH_USER_MODEL)),
                ('reopened_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reopened_period_closures', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'billing_period_closures',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='ClientLedger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('type', models.CharField(db_index=True, max_length=16)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('running_balance', models.DecimalField(decimal_places=2, max_digits=14)),
                ('reference_model', models.CharField(db_index=True, max_length=64)),
                ('reference_id', models.IntegerField(db_index=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('narration', models.TextField(blank=True, null=True)),
                ('status', models.IntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ledger_entries', to='users.client')),
                ('entry_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_ledger_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'billing_client_ledgers',
                'ordering': ['client', '-date', '-id'],
            },
        ),
        migrations.AddIndex(
            model_name='quotation',
            index=models.Index(fields=['client', 'status'], name='billing_quo_client__d05510_idx'),
        ),
        migrations.AddIndex(
            model_name='quotation',
            index=models.Index(fields=['status', '-created_at'], name='billing_quo_status_38cbf0_idx'),
        ),
        migrations.AddIndex(
            model_name='quotation',
            index=models.Index(fields=['lifecycle_status', 'client', 'created_at'], name='billing_quo_lifecyc_d30a84_idx'),
        ),
        migrations.AddIndex(
            model_name='quotationrevision',
            index=models.Index(fields=['quotation', 'revision_number'], name='billing_quo_quotati_fba3ae_idx'),
        ),
        migrations.AddIndex(
            model_name='quotationrevision',
            index=models.Index(fields=['status', 'quotation', '-created_at'], name='billing_quo_status_02f23b_idx'),
        ),
        migrations.AddIndex(
            model_name='orderacknowledgement',
            index=models.Index(fields=['client', 'status'], name='billing_ord_client__5c65f8_idx'),
        ),
        migrations.AddIndex(
            model_name='orderacknowledgement',
            index=models.Index(fields=['lifecycle_status', 'client', 'created_at'], name='billing_ord_lifecyc_8f99e4_idx'),
        ),
        migrations.AddIndex(
            model_name='orderacknowledgement',
            index=models.Index(fields=['sales_person', 'status'], name='billing_ord_sales_p_8a3d31_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['client', 'status'], name='billing_inv_client__e71887_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['status', 'due_date'], name='billing_inv_status_a81a59_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['lifecycle_status', 'client', 'issue_date'], name='billing_inv_lifecyc_83b381_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['contract', 'status'], name='billing_inv_contrac_df7764_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['client', '-payment_date'], name='billing_pay_client__91f422_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['lifecycle_status', 'client', 'payment_date'], name='billing_pay_lifecyc_2d2f70_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentjournal',
            index=models.Index(fields=['client', 'status'], name='billing_pay_client__47f897_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentjournal',
            index=models.Index(fields=['-payment_date', 'status'], name='billing_pay_payment_d61a09_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentjournal',
            index=models.Index(fields=['lifecycle_status', 'client', 'created_at'], name='billing_pay_lifecyc_1955b9_idx'),
        ),
        migrations.AddIndex(
            model_name='clientledger',
            index=models.Index(fields=['client', '-date'], name='billing_cli_client__8d5757_idx'),
        ),
        migrations.AddIndex(
            model_name='clientledger',
            index=models.Index(fields=['reference_model', 'reference_id'], name='billing_cli_referen_9f2705_idx'),
        ),
        migrations.AddIndex(
            model_name='clientledger',
            index=models.Index(fields=['status', 'client', 'date'], name='billing_cli_status_8b3ae0_idx'),
        ),
        migrations.AddIndex(
            model_name='periodclosure',
            index=models.Index(fields=['start_date', 'end_date'], name='billing_per_start_d_973167_idx'),
        ),
        migrations.AddIndex(
            model_name='periodclosure',
            index=models.Index(fields=['status', '-start_date'], name='billing_per_status_d76ae5_idx'),
        ),
        migrations.AddIndex(
            model_name='periodclosure',
            index=models.Index(fields=['financial_year_label', 'start_date'], name='billing_per_financi_3905cf_idx'),
        ),
        migrations.AddIndex(
            model_name='periodclosure',
            index=models.Index(fields=['lifecycle_status', 'status', 'start_date'], name='billing_per_lifecyc_2ad2b8_idx'),
        ),
    ]

