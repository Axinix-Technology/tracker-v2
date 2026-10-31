# Generated for Tracker Agile Collaboration Suite (Clean Baseline)
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. TaskType
        migrations.CreateModel(
            name='TaskType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.CharField(default='Development', max_length=64)),
                ('estimatedHours', models.FloatField(db_column='estimated_hours', default=0)),
                ('icon', models.CharField(blank=True, max_length=64, null=True)),
                ('color', models.CharField(blank=True, max_length=32, null=True)),
                ('status', models.SmallIntegerField(db_index=True, default=1)),
                ('isActive', models.BooleanField(db_column='is_active', db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'task_types',
            },
        ),

        # 2. Sprint
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('goal', models.TextField(blank=True, null=True)),
                ('startDate', models.DateField(db_column='start_date', db_index=True)),
                ('endDate', models.DateField(db_column='end_date', db_index=True)),
                ('state', models.CharField(db_index=True, default='Upcoming', max_length=32)),
                ('velocity', models.FloatField(default=0.0)),
                ('status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('clientId', models.ForeignKey(blank=True, db_column='client_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sprints', to='users.client')),
                ('createdBy', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_sprints', to=settings.AUTH_USER_MODEL)),
                ('projectTypeId', models.ForeignKey(blank=True, db_column='project_type_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sprints', to='users.projecttype')),
            ],
            options={
                'db_table': 'sprints',
            },
        ),

        # 3. Milestone
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('dueDate', models.DateField(blank=True, db_column='due_date', db_index=True, null=True)),
                ('status', models.CharField(db_index=True, default='Pending', max_length=32)),
                ('billingPercentage', models.FloatField(db_column='billing_percentage', default=0.0)),
                ('order', models.PositiveIntegerField(default=1)),
                ('status_code', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('clientId', models.ForeignKey(db_column='client_id', on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='users.client')),
                ('projectTypeId', models.ForeignKey(db_column='project_type_id', on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='users.projecttype')),
            ],
            options={
                'db_table': 'milestones',
            },
        ),

        # 4. Task
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_key', models.CharField(blank=True, db_index=True, max_length=64, null=True, unique=True)),
                ('title', models.CharField(db_index=True, max_length=255)),
                ('isFromTicket', models.BooleanField(db_column='is_from_ticket', db_index=True, default=False)),
                ('userStory', models.TextField(blank=True, db_column='user_story', null=True)),
                ('observation', models.TextField(blank=True, null=True)),
                ('impacts', models.TextField(blank=True, null=True)),
                ('acceptanceCriteria', models.TextField(blank=True, db_column='acceptance_criteria', null=True)),
                ('referenceUrl', models.CharField(blank=True, db_column='reference_url', max_length=512, null=True)),
                ('attachments', models.JSONField(default=list)),
                ('tags', models.JSONField(default=list)),
                ('priorityLevel', models.CharField(db_column='priority_level', db_index=True, default='Medium', max_length=32)),
                ('status', models.CharField(db_index=True, default='Backlogs', max_length=64)),
                ('metaStatus', models.CharField(db_column='meta_status', db_index=True, default='active', max_length=32)),
                ('storyPoints', models.FloatField(db_column='story_points', default=0.0)),
                ('estimatedHours', models.FloatField(db_column='estimated_hours', default=0.0)),
                ('actualHours', models.FloatField(db_column='actual_hours', default=0.0)),
                ('progress', models.PositiveSmallIntegerField(default=0)),
                ('complexity', models.CharField(blank=True, db_index=True, max_length=16, null=True)),
                ('deliveryStage', models.CharField(blank=True, db_column='delivery_stage', db_index=True, max_length=64, null=True)),
                ('stageHistory', models.JSONField(db_column='stage_history', default=list)),
                ('activeJobSessionId', models.PositiveBigIntegerField(blank=True, db_column='active_job_session_id', null=True)),
                ('startDate', models.DateField(blank=True, db_column='start_date', db_index=True, null=True)),
                ('endDate', models.DateField(blank=True, db_column='end_date', db_index=True, null=True)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignedTo', models.ManyToManyField(blank=True, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
                ('assigneeId', models.ForeignKey(blank=True, db_column='assignee_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_tasks', to=settings.AUTH_USER_MODEL)),
                ('blockedBy', models.ManyToManyField(blank=True, related_name='blocking', to='tasks.task')),
                ('clientId', models.ForeignKey(blank=True, db_column='client_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='users.client')),
                ('createdBy', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tasks', to=settings.AUTH_USER_MODEL)),
                ('followers', models.ManyToManyField(blank=True, related_name='followed_tasks', to=settings.AUTH_USER_MODEL)),
                ('milestoneId', models.ForeignKey(blank=True, db_column='milestone_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='tasks.milestone')),
                ('parentTask', models.ForeignKey(blank=True, db_column='parent_task_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subtasks', to='tasks.task')),
                ('projectTypeId', models.ForeignKey(blank=True, db_column='project_type_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='users.projecttype')),
                ('sprintId', models.ForeignKey(blank=True, db_column='sprint_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='tasks.sprint')),
                ('taskTypeId', models.ForeignKey(blank=True, db_column='task_type_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='tasks.tasktype')),
            ],
            options={
                'db_table': 'tasks',
            },
        ),

        # 5. TimeTrackerSession
        migrations.CreateModel(
            name='TimeTrackerSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startTime', models.DateTimeField(db_column='start_time', db_index=True, default=django.utils.timezone.now)),
                ('endTime', models.DateTimeField(blank=True, db_column='end_time', null=True)),
                ('status', models.CharField(db_index=True, default='active', max_length=32)),
                ('duration', models.PositiveIntegerField(default=0)),
                ('pauses', models.JSONField(default=list)),
                ('notes', models.TextField(blank=True, null=True)),
                ('isBillable', models.BooleanField(db_column='is_billable', default=True)),
                ('employeeHourlyRate', models.FloatField(db_column='employee_hourly_rate', default=0.0)),
                ('productionCost', models.FloatField(db_column='production_cost', default=0.0)),
                ('deliveryStageAtStart', models.CharField(blank=True, db_column='delivery_stage_at_start', max_length=64, null=True)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('clientId', models.ForeignKey(blank=True, db_column='client_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='time_sessions', to='users.client')),
                ('projectId', models.ForeignKey(blank=True, db_column='project_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='time_sessions', to='users.projecttype')),
                ('taskId', models.ForeignKey(db_column='task_id', on_delete=django.db.models.deletion.CASCADE, related_name='time_sessions', to='tasks.task')),
                ('userId', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='time_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'time_tracker_sessions',
            },
        ),

        # 6. EmployeeTaskQueue
        migrations.CreateModel(
            name='EmployeeTaskQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('queue', models.JSONField(default=list)),
                ('status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employeeId', models.OneToOneField(db_column='employee_id', on_delete=django.db.models.deletion.CASCADE, related_name='task_queue', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'employee_task_queues',
            },
        ),

        # 7. EmployeeTaskQueueRequest
        migrations.CreateModel(
            name='EmployeeTaskQueueRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requestType', models.CharField(db_column='request_type', default='REORDER', max_length=64)),
                ('status', models.CharField(db_index=True, default='Pending', max_length=32)),
                ('reason', models.TextField(blank=True, null=True)),
                ('lifecycle_status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeId', models.ForeignKey(db_column='employee_id', on_delete=django.db.models.deletion.CASCADE, related_name='queue_requests', to=settings.AUTH_USER_MODEL)),
                ('taskId', models.ForeignKey(db_column='task_id', on_delete=django.db.models.deletion.CASCADE, related_name='queue_requests', to='tasks.task')),
            ],
            options={
                'db_table': 'employee_task_queue_requests',
            },
        ),

        # 8. CommentsThread
        migrations.CreateModel(
            name='CommentsThread',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.JSONField(default=list)),
                ('status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('taskId', models.OneToOneField(db_column='task_id', on_delete=django.db.models.deletion.CASCADE, related_name='comments_thread', to='tasks.task')),
            ],
            options={
                'db_table': 'comments_threads',
            },
        ),

        # 9. Todo
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('completed', models.BooleanField(default=False)),
                ('priority', models.CharField(default='medium', max_length=32)),
                ('dueDate', models.DateField(blank=True, db_column='due_date', null=True)),
                ('status', models.SmallIntegerField(db_index=True, default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employeeId', models.ForeignKey(db_column='employee_id', on_delete=django.db.models.deletion.CASCADE, related_name='todos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'todos',
            },
        ),

        # 10. Indexes
        migrations.AddIndex(
            model_name='sprint',
            index=models.Index(fields=['status', 'state', 'startDate'], name='sprints_status_223a5b_idx'),
        ),
        migrations.AddIndex(
            model_name='sprint',
            index=models.Index(fields=['clientId', 'projectTypeId'], name='sprints_client__eee0c1_idx'),
        ),
        migrations.AddIndex(
            model_name='milestone',
            index=models.Index(fields=['status_code', 'clientId', 'status'], name='milestones_status__53d867_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['lifecycle_status', 'status', 'clientId'], name='tasks_lifecyc_e0a95e_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['lifecycle_status', 'status', 'sprintId'], name='tasks_lifecyc_795530_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['lifecycle_status', 'assigneeId', 'priorityLevel'], name='tasks_lifecyc_7c07a4_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['startDate', 'endDate'], name='tasks_start_d_d24fb5_idx'),
        ),
        migrations.AddIndex(
            model_name='timetrackersession',
            index=models.Index(fields=['lifecycle_status', 'userId', 'status'], name='time_tracke_lifecyc_65dc47_idx'),
        ),
        migrations.AddIndex(
            model_name='timetrackersession',
            index=models.Index(fields=['lifecycle_status', 'taskId', 'status'], name='time_tracke_lifecyc_2df5d1_idx'),
        ),
    ]
