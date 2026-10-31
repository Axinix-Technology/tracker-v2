from django.db import models
from django.conf import settings
from django.utils import timezone
from populate_core.registry import register_model

# ============================================================================
# 1. TASK TYPE & SPRINT
# ============================================================================

@register_model("task_type", table_type="master", aliases=["task_types", "tasktypes"])
class TaskType(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=64, default="Development")
    estimatedHours = models.FloatField(default=0, db_column="estimated_hours")
    icon = models.CharField(max_length=64, blank=True, null=True)
    color = models.CharField(max_length=32, blank=True, null=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    isActive = models.BooleanField(default=True, db_column="is_active", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_types"

    def __str__(self):
        return self.name


@register_model("sprint", table_type="master", aliases=["sprints"])
class Sprint(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    goal = models.TextField(blank=True, null=True)
    startDate = models.DateField(db_column="start_date", db_index=True)
    endDate = models.DateField(db_column="end_date", db_index=True)
    state = models.CharField(max_length=32, default="Upcoming", db_index=True)  # Upcoming, Active, Completed, Closed
    velocity = models.FloatField(default=0.0)
    clientId = models.ForeignKey("users.Client", on_delete=models.SET_NULL, null=True, blank=True, db_column="client_id", related_name="sprints")
    projectTypeId = models.ForeignKey("users.ProjectType", on_delete=models.SET_NULL, null=True, blank=True, db_column="project_type_id", related_name="sprints")
    createdBy = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column="created_by", related_name="created_sprints")
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sprints"
        indexes = [
            models.Index(fields=["status", "state", "startDate"]),
            models.Index(fields=["clientId", "projectTypeId"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.state})"

    @property
    def client(self): return self.clientId
    @property
    def project_type(self): return self.projectTypeId


# ============================================================================
# 2. MILESTONE
# ============================================================================

@register_model("milestone", table_type="master", aliases=["milestones"])
class Milestone(models.Model):
    title = models.CharField(max_length=255)
    clientId = models.ForeignKey("users.Client", on_delete=models.CASCADE, db_column="client_id", related_name="milestones")
    projectTypeId = models.ForeignKey("users.ProjectType", on_delete=models.CASCADE, db_column="project_type_id", related_name="milestones")
    description = models.TextField(blank=True, null=True)
    dueDate = models.DateField(blank=True, null=True, db_column="due_date", db_index=True)
    status = models.CharField(max_length=32, default="Pending", db_index=True)
    billingPercentage = models.FloatField(default=0.0, db_column="billing_percentage")
    order = models.PositiveIntegerField(default=1)
    status_code = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "milestones"
        indexes = [
            models.Index(fields=["status_code", "clientId", "status"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"


# ============================================================================
# 3. TASK (JIRA-RIVAL AGILE ENTITY)
# ============================================================================

@register_model(
    "task",
    table_type="transaction",
    status_field="lifecycle_status",
    aliases=["tasks"]
)
class Task(models.Model):
    task_key = models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255, db_index=True)
    clientId = models.ForeignKey("users.Client", on_delete=models.SET_NULL, null=True, blank=True, db_column="client_id", related_name="tasks")
    projectTypeId = models.ForeignKey("users.ProjectType", on_delete=models.SET_NULL, null=True, blank=True, db_column="project_type_id", related_name="tasks")
    taskTypeId = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True, db_column="task_type_id", related_name="tasks")
    sprintId = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, db_column="sprint_id", related_name="tasks")
    milestoneId = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True, db_column="milestone_id", related_name="tasks")
    
    # Hierarchy: Epic / Story / Subtask
    parentTask = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, db_column="parent_task_id", related_name="subtasks")
    
    # Dependencies: blocks / is_blocked_by
    blockedBy = models.ManyToManyField("self", symmetrical=False, related_name="blocking", blank=True)

    # Assignees & Followers
    assignedTo = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="assigned_tasks")
    assigneeId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column="assignee_id", related_name="primary_tasks")
    createdBy = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column="created_by", related_name="created_tasks")
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="followed_tasks")

    # Ticket integration
    linkedTicketId = models.ForeignKey("tickets.Ticket", on_delete=models.SET_NULL, null=True, blank=True, db_column="linked_ticket_id", related_name="linked_tasks")
    isFromTicket = models.BooleanField(default=False, db_column="is_from_ticket", db_index=True)

    # Spec details
    userStory = models.TextField(blank=True, null=True, db_column="user_story")
    observation = models.TextField(blank=True, null=True)
    impacts = models.TextField(blank=True, null=True)
    acceptanceCriteria = models.TextField(blank=True, null=True, db_column="acceptance_criteria")
    referenceUrl = models.CharField(max_length=512, blank=True, null=True, db_column="reference_url")
    attachments = models.JSONField(default=list)
    tags = models.JSONField(default=list)

    # Agile Metrics & Progress
    priorityLevel = models.CharField(max_length=32, default="Medium", db_index=True, db_column="priority_level")
    status = models.CharField(max_length=64, default="Backlogs", db_index=True)
    metaStatus = models.CharField(max_length=32, default="active", db_index=True, db_column="meta_status")
    storyPoints = models.FloatField(default=0.0, db_column="story_points")
    estimatedHours = models.FloatField(default=0.0, db_column="estimated_hours")
    actualHours = models.FloatField(default=0.0, db_column="actual_hours")
    progress = models.PositiveSmallIntegerField(default=0)
    complexity = models.CharField(max_length=16, blank=True, null=True, db_index=True)
    deliveryStage = models.CharField(max_length=64, blank=True, null=True, db_index=True, db_column="delivery_stage")

    # Work State History
    stageHistory = models.JSONField(default=list, db_column="stage_history")
    activeJobSessionId = models.PositiveBigIntegerField(blank=True, null=True, db_column="active_job_session_id")

    startDate = models.DateField(blank=True, null=True, db_column="start_date", db_index=True)
    endDate = models.DateField(blank=True, null=True, db_column="end_date", db_index=True)

    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"
        indexes = [
            models.Index(fields=["lifecycle_status", "status", "clientId"]),
            models.Index(fields=["lifecycle_status", "status", "sprintId"]),
            models.Index(fields=["lifecycle_status", "assigneeId", "priorityLevel"]),
            models.Index(fields=["startDate", "endDate"]),
        ]

    def __str__(self):
        prefix = f"[{self.task_key}] " if self.task_key else ""
        return f"{prefix}{self.title} ({self.status})"

    @property
    def client(self): return self.clientId
    @property
    def project_type(self): return self.projectTypeId
    @property
    def task_type(self): return self.taskTypeId
    @property
    def sprint(self): return self.sprintId
    @property
    def assignee(self): return self.assigneeId
    @property
    def created_by(self): return self.createdBy
    @property
    def name(self): return self.title
    @property
    def priority(self): return self.priorityLevel


# ============================================================================
# 4. TIME TRACKER SESSION (LIVE WORK TRACKING)
# ============================================================================

@register_model(
    "time_tracker_session",
    table_type="transaction",
    status_field="lifecycle_status",
    aliases=["time_tracker_sessions", "timetrackersession"]
)
class TimeTrackerSession(models.Model):
    taskId = models.ForeignKey(Task, on_delete=models.CASCADE, db_column="task_id", related_name="time_sessions")
    userId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="user_id", related_name="time_sessions")
    projectId = models.ForeignKey("users.ProjectType", on_delete=models.SET_NULL, null=True, blank=True, db_column="project_id", related_name="time_sessions")
    clientId = models.ForeignKey("users.Client", on_delete=models.SET_NULL, null=True, blank=True, db_column="client_id", related_name="time_sessions")
    
    startTime = models.DateTimeField(default=timezone.now, db_column="start_time", db_index=True)
    endTime = models.DateTimeField(blank=True, null=True, db_column="end_time")
    status = models.CharField(max_length=32, default="active", db_index=True)  # active, paused, completed
    duration = models.PositiveIntegerField(default=0)  # Total worked seconds
    pauses = models.JSONField(default=list)  # [{ pausedAt, resumedAt, duration }]
    notes = models.TextField(blank=True, null=True)

    isBillable = models.BooleanField(default=True, db_column="is_billable")
    employeeHourlyRate = models.FloatField(default=0.0, db_column="employee_hourly_rate")
    productionCost = models.FloatField(default=0.0, db_column="production_cost")
    deliveryStageAtStart = models.CharField(max_length=64, blank=True, null=True, db_column="delivery_stage_at_start")
    
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "time_tracker_sessions"
        indexes = [
            models.Index(fields=["lifecycle_status", "userId", "status"]),
            models.Index(fields=["lifecycle_status", "taskId", "status"]),
        ]

    def __str__(self):
        return f"{self.userId} on {self.taskId} ({self.status}) - {self.duration}s"

    @property
    def task(self): return self.taskId
    @property
    def user(self): return self.userId


# ============================================================================
# 5. EMPLOYEE TASK QUEUE & REQUESTS
# ============================================================================

@register_model("employee_task_queue", table_type="master", aliases=["employee_task_queues", "employeetaskqueue"])
class EmployeeTaskQueue(models.Model):
    employeeId = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="employee_id", related_name="task_queue")
    queue = models.JSONField(default=list)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "employee_task_queues"

    def __str__(self):
        return f"Task Queue for {self.employeeId}"


@register_model(
    "employee_task_queue_request",
    table_type="transaction",
    status_field="lifecycle_status",
    aliases=["employee_task_queue_requests", "employeetaskqueuerequest"]
)
class EmployeeTaskQueueRequest(models.Model):
    employeeId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="employee_id", related_name="queue_requests")
    taskId = models.ForeignKey(Task, on_delete=models.CASCADE, db_column="task_id", related_name="queue_requests")
    requestType = models.CharField(max_length=64, default="REORDER", db_column="request_type")
    status = models.CharField(max_length=32, default="Pending", db_index=True)
    reason = models.TextField(blank=True, null=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employee_task_queue_requests"

    def __str__(self):
        return f"{self.employeeId} queue request on {self.taskId}"


# ============================================================================
# 6. COMMENTS THREAD
# ============================================================================

@register_model("comments_thread", table_type="transaction", aliases=["comments_threads", "commentsthread"])
class CommentsThread(models.Model):
    taskId = models.OneToOneField(Task, on_delete=models.CASCADE, db_column="task_id", related_name="comments_thread")
    comments = models.JSONField(default=list)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments_threads"

    def __str__(self):
        return f"Comments for {self.taskId}"


# ============================================================================
# 7. TODOS
# ============================================================================

@register_model("todo", table_type="transaction", aliases=["todos"])
class Todo(models.Model):
    employeeId = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column="employee_id", related_name="todos")
    text = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=32, default="medium")
    dueDate = models.DateField(blank=True, null=True, db_column="due_date")
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "todos"

    def __str__(self):
        return self.text

    @property
    def employee(self): return self.employeeId


# ============================================================================
# 8. DAILY ACTIVITY (TIMESHEET & DAILY WORK LOG)
# ============================================================================

@register_model(
    "daily_activity",
    table_type="transaction",
    status_field="lifecycle_status",
    aliases=["daily_activities", "dailyactivity"]
)
class DailyActivity(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_activities"
    )
    client = models.ForeignKey(
        "users.Client",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="daily_activities"
    )
    project_type = models.ForeignKey(
        "users.ProjectType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="daily_activities"
    )
    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="daily_activities"
    )
    date = models.DateField(default=timezone.now, db_index=True)
    activity = models.TextField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_daily_activities"
    )
    status = models.CharField(max_length=64, default="Pending", db_index=True)
    meta_status = models.CharField(max_length=32, default="active", db_index=True)
    lifecycle_status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "daily_activities"
        indexes = [
            models.Index(fields=["lifecycle_status", "user", "date"]),
            models.Index(fields=["lifecycle_status", "date", "status"]),
            models.Index(fields=["lifecycle_status", "client", "date"]),
            models.Index(fields=["lifecycle_status", "assigned_to", "status"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.date}: {self.activity[:40]}"

    @property
    def clientId(self):
        return self.client

    @property
    def projectTypeId(self):
        return self.project_type

    @property
    def taskTypeId(self):
        return self.task_type

    @property
    def assignedTo(self):
        return self.assigned_to

