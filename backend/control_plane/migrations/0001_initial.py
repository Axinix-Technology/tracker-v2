import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_id', models.CharField(db_index=True, max_length=64, unique=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True, null=True)),
                ('collections', models.JSONField(default=list, help_text='Registered model names granted under this module')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'control_plane_modules',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tenant_id', models.CharField(db_index=True, max_length=64, unique=True)),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('subdomain', models.CharField(db_index=True, max_length=128, unique=True)),
                ('database_name', models.CharField(max_length=128, unique=True)),
                ('plan', models.CharField(default='Enterprise', max_length=64)),
                ('status', models.CharField(db_index=True, default='Active', max_length=32)),
                ('enabled_modules', models.JSONField(default=list, help_text="e.g. ['hrms', 'attendance', 'payroll', 'billing', 'crm', 'recruitment']")),
                ('settings', models.JSONField(default=dict)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'control_plane_tenants',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ProvisioningRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('database_name', models.CharField(max_length=128)),
                ('status', models.CharField(db_index=True, default='Pending', max_length=32)),
                ('steps_completed', models.JSONField(default=list)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('initiated_by', models.CharField(default='System', max_length=128)),
                ('started_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provisioning_runs', to='control_plane.tenant')),
            ],
            options={
                'db_table': 'control_plane_provisioning_runs',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='UserLogin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('user_id', models.IntegerField(db_index=True, help_text='Primary key of user inside tenant database')),
                ('is_superadmin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_logins', to='control_plane.tenant')),
            ],
            options={
                'db_table': 'control_plane_user_logins',
            },
        ),
        migrations.AddIndex(
            model_name='tenant',
            index=models.Index(fields=['status', 'subdomain'], name='control_pla_status_7a18bc_idx'),
        ),
        migrations.AddIndex(
            model_name='tenant',
            index=models.Index(fields=['lifecycle_status', 'status'], name='control_pla_lifecyc_0188ea_idx'),
        ),
        migrations.AddIndex(
            model_name='provisioningrun',
            index=models.Index(fields=['tenant', 'status'], name='control_pla_tenant__a8123b_idx'),
        ),
        migrations.AddIndex(
            model_name='provisioningrun',
            index=models.Index(fields=['started_at', 'status'], name='control_pla_started_8172ea_idx'),
        ),
        migrations.AddIndex(
            model_name='userlogin',
            index=models.Index(fields=['email', 'is_active'], name='control_pla_email_8a123f_idx'),
        ),
        migrations.AddIndex(
            model_name='userlogin',
            index=models.Index(fields=['tenant', 'is_active'], name='control_pla_tenant__1928ae_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='userlogin',
            unique_together={('email', 'tenant')},
        ),
    ]

