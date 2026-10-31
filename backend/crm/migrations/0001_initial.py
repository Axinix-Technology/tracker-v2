import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0002_basicinfo_professionalinfo'),
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=128, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(db_index=True, default='Active', max_length=16)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'crm_lead_types',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ReferenceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=128, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(db_index=True, default='Active', max_length=16)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'crm_reference_types',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(db_index=True, max_length=128)),
                ('last_name', models.CharField(blank=True, max_length=128, null=True)),
                ('company_name', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, db_index=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, db_index=True, max_length=32, null=True)),
                ('designation', models.CharField(blank=True, max_length=128, null=True)),
                ('source', models.CharField(blank=True, max_length=128, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('contacted_at', models.DateTimeField(blank=True, null=True)),
                ('contact_history', models.JSONField(default=list, help_text='Historical log')),
                ('status', models.CharField(db_index=True, default='New', max_length=32)),
                ('meta_status', models.CharField(db_index=True, default='active', max_length=32)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('tags', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_contacts', to=settings.AUTH_USER_MODEL)),
                ('contacted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contacted_records', to=settings.AUTH_USER_MODEL)),
                ('converted_client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='originating_contacts', to='users.client')),
                ('lead_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contacts', to='crm.leadtype')),
                ('reference_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contacts', to='crm.referencetype')),
            ],
            options={
                'db_table': 'crm_contacts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('stage', models.CharField(db_index=True, default='New', max_length=32)),
                ('expected_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=14)),
                ('probability', models.SmallIntegerField(default=10, help_text='0-100 percentage probability')),
                ('expected_close_date', models.DateField(blank=True, db_index=True, null=True)),
                ('actual_close_date', models.DateField(blank=True, null=True)),
                ('lost_reason', models.TextField(blank=True, null=True)),
                ('competitor', models.CharField(blank=True, max_length=255, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('tags', models.JSONField(default=list)),
                ('meta_status', models.CharField(db_index=True, default='active', max_length=32)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to='users.client')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='opportunities', to='crm.contact')),
                ('contract', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='linked_opportunities', to='billing.orderacknowledgement')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_opportunities', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='owned_opportunities', to=settings.AUTH_USER_MODEL)),
                ('project_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='opportunities', to='users.projecttype')),
                ('quotation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='linked_opportunities', to='billing.quotation')),
            ],
            options={
                'db_table': 'crm_opportunities',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CRMActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(db_index=True, default='Note', max_length=32)),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('metadata', models.JSONField(default=dict)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crm_activities', to='users.client')),
                ('performed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='performed_crm_activities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'crm_activities',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='CRMMeeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('scheduled_time', models.DateTimeField(db_index=True)),
                ('end_time', models.DateTimeField()),
                ('actual_start_time', models.DateTimeField(blank=True, null=True)),
                ('actual_end_time', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(db_index=True, default='Scheduled', max_length=32)),
                ('outcome', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('attendees', models.ManyToManyField(blank=True, related_name='crm_meetings', to=settings.AUTH_USER_MODEL)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crm_meetings', to='users.client')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_crm_meetings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'crm_meetings',
                'ordering': ['-scheduled_time'],
            },
        ),
        migrations.AddIndex(
            model_name='leadtype',
            index=models.Index(fields=['status', 'name'], name='crm_lead_ty_status_fa018c_idx'),
        ),
        migrations.AddIndex(
            model_name='leadtype',
            index=models.Index(fields=['lifecycle_status', 'status'], name='crm_lead_ty_lifecyc_0188ef_idx'),
        ),
        migrations.AddIndex(
            model_name='referencetype',
            index=models.Index(fields=['status', 'name'], name='crm_referen_status_827ef1_idx'),
        ),
        migrations.AddIndex(
            model_name='referencetype',
            index=models.Index(fields=['lifecycle_status', 'status'], name='crm_referen_lifecyc_1928df_idx'),
        ),
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['status', 'assigned_to'], name='crm_contact_status_7a81b2_idx'),
        ),
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['company_name', 'status'], name='crm_contact_company_198e3b_idx'),
        ),
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['lifecycle_status', 'status', 'created_at'], name='crm_contact_lifecyc_d837ea_idx'),
        ),
        migrations.AddIndex(
            model_name='opportunity',
            index=models.Index(fields=['account', 'stage'], name='crm_opportu_account_a6f3b0_idx'),
        ),
        migrations.AddIndex(
            model_name='opportunity',
            index=models.Index(fields=['owner', 'stage'], name='crm_opportu_owner_i_1e98bc_idx'),
        ),
        migrations.AddIndex(
            model_name='opportunity',
            index=models.Index(fields=['stage', 'expected_close_date'], name='crm_opportu_stage_d8e09f_idx'),
        ),
        migrations.AddIndex(
            model_name='opportunity',
            index=models.Index(fields=['lifecycle_status', 'stage', '-expected_value'], name='crm_opportu_lifecyc_8123ae_idx'),
        ),
        migrations.AddIndex(
            model_name='crmactivity',
            index=models.Index(fields=['client', '-timestamp'], name='crm_activit_client__b591b2_idx'),
        ),
        migrations.AddIndex(
            model_name='crmactivity',
            index=models.Index(fields=['lifecycle_status', 'client', '-timestamp'], name='crm_activit_lifecyc_8a2bf1_idx'),
        ),
        migrations.AddIndex(
            model_name='crmmeeting',
            index=models.Index(fields=['scheduled_time', 'status'], name='crm_meeting_schedul_a91b28_idx'),
        ),
        migrations.AddIndex(
            model_name='crmmeeting',
            index=models.Index(fields=['client', 'status'], name='crm_meeting_client__e781c2_idx'),
        ),
        migrations.AddIndex(
            model_name='crmmeeting',
            index=models.Index(fields=['lifecycle_status', 'status', 'scheduled_time'], name='crm_meeting_lifecyc_39e102_idx'),
        ),
    ]

