import django.db.models.deletion
import django.utils.timezone
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
            name='EmailConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(default='gmail', max_length=32)),
                ('host', models.CharField(max_length=255)),
                ('port', models.IntegerField(default=587)),
                ('secure', models.BooleanField(default=False)),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('from_name', models.CharField(max_length=128)),
                ('from_email', models.EmailField(max_length=254)),
                ('enabled', models.BooleanField(db_index=True, default=True)),
                ('status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'system_email_configs',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
                ('code', models.CharField(db_index=True, max_length=64, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.CharField(default='Software', max_length=128)),
                ('unit_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=18.0, max_digits=5)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'system_products',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, help_text='Frontend can() target key', max_length=128, unique=True)),
                ('model_name', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('display_name', models.CharField(max_length=128)),
                ('module', models.CharField(db_index=True, default='general', max_length=64)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'system_resources',
                'ordering': ['module', 'key'],
            },
        ),
        migrations.CreateModel(
            name='StatusConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(db_index=True, max_length=128, unique=True)),
                ('label', models.CharField(max_length=128)),
                ('meta_statuses', models.JSONField(default=list, help_text='Key, label, color, order, isDefault')),
                ('workflow_statuses', models.JSONField(default=list, help_text='Key, label, color, order, isDefault, isTerminal, isSequential')),
                ('status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'system_status_configs',
                'ordering': ['model_name'],
            },
        ),
        migrations.CreateModel(
            name='ReleaseNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(db_index=True, max_length=64)),
                ('release_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('title', models.CharField(max_length=255)),
                ('tagline', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(default='Feature & Maintenance Release', max_length=64)),
                ('is_latest', models.BooleanField(db_index=True, default=False)),
                ('is_published', models.BooleanField(db_index=True, default=True)),
                ('categories', models.JSONField(default=dict, help_text='Features, improvements, security, fixes')),
                ('seen_by', models.JSONField(default=list, help_text='[{ employeeId, viewedAt }]')),
                ('meta_status', models.CharField(db_index=True, default='active', max_length=32)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_release_notes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'system_release_notes',
                'ordering': ['-release_date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('contact_person', models.CharField(blank=True, max_length=128, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=32, null=True)),
                ('address', models.JSONField(default=dict)),
                ('gst_in', models.CharField(blank=True, max_length=32, null=True)),
                ('pan_number', models.CharField(blank=True, max_length=32, null=True)),
                ('bank_details', models.JSONField(default=dict)),
                ('status', models.CharField(db_index=True, default='Active', max_length=16)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('services', models.ManyToManyField(blank=True, related_name='service_providers', to='users.projecttype')),
            ],
            options={
                'db_table': 'system_service_providers',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='StatusMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_model', models.CharField(db_index=True, max_length=128)),
                ('target_model', models.CharField(db_index=True, max_length=128)),
                ('link_field', models.CharField(default='linkedTicketId', max_length=128)),
                ('reverse_link_field', models.CharField(default='linkedTaskId', max_length=128)),
                ('mappings', models.JSONField(default=list, help_text='List of status mappings')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'system_status_mappings',
            },
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('model_name', models.CharField(db_index=True, max_length=128)),
                ('trigger_type', models.CharField(db_index=True, max_length=64)),
                ('conditions', models.JSONField(default=dict, help_text='{ departmentId, priorityLevel }')),
                ('steps', models.JSONField(default=list, help_text='List of steps')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_workflows', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'system_workflows',
                'ordering': ['model_name', 'name'],
            },
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['is_active', 'name'], name='system_prod_is_acti_07b9a1_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['lifecycle_status', 'is_active'], name='system_prod_lifecyc_017b28_idx'),
        ),
        migrations.AddIndex(
            model_name='resource',
            index=models.Index(fields=['module', 'is_active'], name='system_reso_module_8123af_idx'),
        ),
        migrations.AddIndex(
            model_name='resource',
            index=models.Index(fields=['lifecycle_status', 'is_active'], name='system_reso_lifecyc_7c29be_idx'),
        ),
        migrations.AddIndex(
            model_name='releasenote',
            index=models.Index(fields=['is_published', 'is_latest'], name='system_rele_is_publ_97ef2a_idx'),
        ),
        migrations.AddIndex(
            model_name='releasenote',
            index=models.Index(fields=['version', 'is_published'], name='system_rele_version_b723ea_idx'),
        ),
        migrations.AddIndex(
            model_name='serviceprovider',
            index=models.Index(fields=['status', 'name'], name='system_serv_status_3d81b2_idx'),
        ),
        migrations.AddIndex(
            model_name='serviceprovider',
            index=models.Index(fields=['lifecycle_status', 'status'], name='system_serv_lifecyc_8123ae_idx'),
        ),
        migrations.AddIndex(
            model_name='statusmapping',
            index=models.Index(fields=['source_model', 'target_model'], name='system_stat_source__19e2bf_idx'),
        ),
        migrations.AddIndex(
            model_name='statusmapping',
            index=models.Index(fields=['is_active', 'status'], name='system_stat_is_acti_48f12a_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='statusmapping',
            unique_together={('source_model', 'target_model')},
        ),
        migrations.AddIndex(
            model_name='workflow',
            index=models.Index(fields=['model_name', 'trigger_type', 'is_active'], name='system_work_model_n_08ab12_idx'),
        ),
        migrations.AddIndex(
            model_name='workflow',
            index=models.Index(fields=['lifecycle_status', 'is_active'], name='system_work_lifecyc_9124cb_idx'),
        ),
    ]

