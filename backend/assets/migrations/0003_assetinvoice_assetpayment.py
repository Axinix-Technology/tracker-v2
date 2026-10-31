import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0002_alter_assetincident_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(db_index=True, max_length=128, unique=True)),
                ('invoice_date', models.DateField()),
                ('due_date', models.DateField(db_index=True)),
                ('sub_total', models.DecimalField(decimal_places=2, max_digits=14)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=14)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('status', models.CharField(db_index=True, default='Pending', max_length=32)),
                ('meta_status', models.CharField(db_index=True, default='active', max_length=32)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='assets.assetpurchase')),
            ],
            options={
                'db_table': 'assets_invoices',
                'ordering': ['-invoice_date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='AssetPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_date', models.DateField(db_index=True, default=django.utils.timezone.now)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=14)),
                ('payment_mode', models.CharField(default='Bank Transfer', max_length=64)),
                ('transaction_ref', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('status', models.CharField(db_index=True, default='Success', max_length=32)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='assets.assetinvoice')),
            ],
            options={
                'db_table': 'assets_payments',
                'ordering': ['-payment_date', '-id'],
            },
        ),
        migrations.AddIndex(
            model_name='assetinvoice',
            index=models.Index(fields=['status', 'due_date'], name='assets_invo_status_2aa561_idx'),
        ),
        migrations.AddIndex(
            model_name='assetinvoice',
            index=models.Index(fields=['purchase', 'status'], name='assets_invo_purchas_ce9efd_idx'),
        ),
        migrations.AddIndex(
            model_name='assetinvoice',
            index=models.Index(fields=['lifecycle_status', 'status', 'created_at'], name='assets_invo_lifecyc_0188b2_idx'),
        ),
        migrations.AddIndex(
            model_name='assetpayment',
            index=models.Index(fields=['invoice', 'status'], name='assets_paym_invoice_d04c26_idx'),
        ),
        migrations.AddIndex(
            model_name='assetpayment',
            index=models.Index(fields=['payment_date', 'status'], name='assets_paym_payment_3a7587_idx'),
        ),
        migrations.AddIndex(
            model_name='assetpayment',
            index=models.Index(fields=['lifecycle_status', 'status', 'payment_date'], name='assets_paym_lifecyc_bb7cb9_idx'),
        ),
    ]

