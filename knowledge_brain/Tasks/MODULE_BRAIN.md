# Tasks & Agile Collaboration Suite — Module Brain

## Overview
The **Project & Agile Collaboration Suite** is a Jira-rival platform built on Django and powered by `django-populate-core` on MySQL (`workhub_db`). It provides full agile sprint lifecycle management, nested task hierarchies (Epics, Stories, Subtasks), DAG dependencies, precision live job tracking (`TimeTrackerSession`), personal work queues (`EmployeeTaskQueue`), project milestones, and ticket synchronization.

---

## Backend Models (`backend_django/tasks/models.py`)

| Model | Table | Key Fields | Purpose |
|---|---|---|---|
| **TaskType** | `task_types` | `name`, `category`, `estimatedHours`, `color`, `icon`, `isActive`, `status` | Configurable task categories (Development, Bug, Feature, Spike). |
| **Sprint** | `sprints` | `name`, `goal`, `startDate`, `endDate`, `state`, `velocity`, `clientId`, `projectTypeId` | Agile sprint lifecycle (Upcoming, Active, Completed, Closed). |
| **Milestone** | `milestones` | `title`, `dueDate`, `billingPercentage`, `status`, `clientId`, `projectTypeId` | Client milestone tracking with billing percentage alignment. |
| **Task** | `tasks` | `task_key`, `title`, `parentTask`, `blockedBy`, `assignedTo`, `assigneeId`, `followers`, `storyPoints`, `estimatedHours`, `actualHours`, `progress`, `stageHistory`, `activeJobSessionId`, `linkedTicketId`, `isFromTicket`, `status`, `metaStatus`, `lifecycle_status` | Jira-rival core agile issue entity with infinite DAG nesting and status tracking. |
| **TimeTrackerSession** | `time_tracker_sessions` | `taskId`, `userId`, `startTime`, `endTime`, `duration`, `pauses` (JSON), `isBillable`, `employeeHourlyRate`, `productionCost`, `status` | Real-time work session tracking with pause interval deduction and production cost derivation. |
| **EmployeeTaskQueue** | `employee_task_queues` | `employeeId`, `queue` (JSON array of task IDs), `status` | Employee's ordered personal backlog for drag-and-drop execution. |
| **EmployeeTaskQueueRequest** | `employee_task_queue_requests` | `employeeId`, `taskId`, `requestType`, `reason`, `status` | Formal approval requests to reprioritize personal queues. |
| **CommentsThread** | `comments_threads` | `taskId`, `comments` (JSON array of UUID-keyed comments) | Dedicated threaded discussion per task with `@mention` parsing. |
| **Todo** | `todos` | `employeeId`, `text`, `completed`, `dueDate`, `priority`, `status` | Lightweight personal checklist items. |

---

## Domain Services & Lifecycle Hooks (`backend_django/tasks/services.py`)

1. **`TaskService` (`@register_service("task")`)**:
   - `before_create`:
     - Auto-generates sequential Jira-style issue keys (`AXN-1`, `AXN-2`, etc.).
     - Prevents circular self-parenting on create.
     - Initializes `stageHistory`: `[{"stage": "Backlogs", "enteredAt": now, "duration": 0}]`.
     - Assigns `createdBy = context.user`.
     - Flags `isFromTicket = True` if linked to a ticket.
   - `before_update`:
     - Prevents setting `parentTask` equal to `instance.id`.
     - Accurately computes duration of the prior stage in seconds upon status transitions and appends the new stage to `stageHistory`.
     - Auto-sets `progress = 100` when marked `Done`/`Completed`.
   - `after_create`:
     - Auto-initializes dedicated `CommentsThread(taskId=instance)`.
     - Enqueues task ID into the assignee's `EmployeeTaskQueue`.
     - Uses `transaction.on_commit` to dispatch push notifications to the assignee and sync linked `Ticket.ticket_status` to `"In Progress"`.
   - `after_update`:
     - Uses `transaction.on_commit` to notify assignees/followers, and auto-resolves linked tickets when the task reaches `"Done"` / `"Completed"`.

2. **`TimeTrackerSessionService` (`@register_service("time_tracker_session")`)**:
   - `before_create`:
     - Auto-pauses any concurrent active sessions for the user to prevent multi-job collisions.
     - Populates `projectId` and `clientId` from the parent task.
   - `before_update`:
     - Handles pause intervals (`pauses` JSON) with precise timestamps (`pausedAt`, `resumedAt`, `duration`).
     - Upon completion, calculates net worked seconds excluding all pause intervals and derives `productionCost = (duration / 3600.0) * employeeHourlyRate`.
   - `after_create`:
     - Points `Task.activeJobSessionId` to the active session and auto-transitions tasks in `Backlogs`/`To Do` to `In Progress`.
   - `after_update`:
     - Upon completion, clears `Task.activeJobSessionId` and uses `transaction.on_commit` to aggregate all completed sessions for this task and atomically write `Task.actualHours`.

3. **`SprintService` (`@register_service("sprint")`)**:
   - Enforces `startDate <= endDate`.
   - Computes completed sprint `velocity` by summing `storyPoints` of all completed tasks in the sprint upon transition to `Completed`.

4. **`CommentsThreadService` (`@register_service("comments_thread")`)**:
   - St হওয়ায় UUIDs, author IDs, and ISO timestamps on all appended comment items.
   - Uses `transaction.on_commit` to scan `@username` mentions and dispatch notifications.

5. **`EmployeeTaskQueueService` & `RequestService`**:
   - Enforces deduplication of task IDs in the queue and applies manager-approved queue reorders.

---

## API Endpoints via Populate Pipeline

All entities execute cleanly through `/api/populate/:action/:model`:
- **Read Tasks with Deep Population**:
  ```http
  POST /api/populate/read/task/
  Content-Type: application/json

  {
    "filter": { "sprintId": 1 },
    "populateFields": {
      "parentTask": "title,task_key",
      "sprintId": "name,goal",
      "assigneeId": "username,email",
      "taskTypeId": "name,color"
    }
  }
  ```
- **Start Timer Session**:
  ```http
  POST /api/populate/create/time_tracker_session/
  Content-Type: application/json

  {
    "taskId": 2,
    "employeeHourlyRate": 45.0
  }
  ```
- **Complete Session**:
  ```http
  POST /api/populate/update/time_tracker_session/<id>/
  Content-Type: application/json

  {
    "status": "completed",
    "notes": "Finished feature implementation"
  }
  ```

---

## Database Indexes (MySQL Engine)
- `tasks`:
  - `(lifecycle_status, status, client_id)`
  - `(lifecycle_status, status, sprint_id)`
  - `(lifecycle_status, assignee_id, priority_level)`
  - `(start_date, end_date)`
- `time_tracker_sessions`:
  - `(lifecycle_status, user_id, status)`
  - `(lifecycle_status, task_id, status)`
- `sprints`:
  - `(status, state, start_date)`
  - `(client_id, project_type_id)`
- `milestones`:
  - `(status_code, client_id, status)`
