# Tickets & Client Support Module — Module Brain

## Overview
The **Tickets & Client Support Module** manages customer issue logging, public and internal support discussions, attachment management, watcher/participant subscriptions, and bi-directional status synchronization with development `Task`s. It runs on Django and MySQL (`workhub_db`), executed seamlessly through the declarative `django-populate-core` pipeline.

---

## 🗄️ Backend Models (`backend_django/tickets/models.py`)

| Model | Table | Description | Key Fields | Relationships |
| :--- | :--- | :--- | :--- | :--- |
| **Ticket** | `tickets` | Main customer support issue. | `ticket_id` (`TCK-1`), `title`, `priority`, `ticket_status`, `meta_status`, `resolved_at`, `closed_at`, `status` | Ref: `users.Client`, `users.ProjectType`, `User` (created_by, assignee), `tasks.Task` (linked_task) |
| **TicketComment** | `ticket_comments` | Public discussion & internal developer notes. | `content`, `is_internal`, `status`, `created_at` | Ref: `Ticket`, `User` (author) |
| **TicketAttachment** | `ticket_attachments` | Uploaded screenshots, documents, and logs. | `file_url`, `file_name`, `file_size`, `status` | Ref: `Ticket`, `User` (uploaded_by) |
| **TicketActivityLog** | `ticket_activity_logs` | Audit trail of all actions and state changes. | `action` (`created`, `assigned`, `status_changed`, `comment_added`), `details` (JSON) | Ref: `Ticket`, `User` (performed_by) |
| **TicketParticipant** | `ticket_participants` | Watchers, assignees, and creators subscribed to notifications. | `role` (`creator`, `assignee`, `watcher`, `manager`), `status` | Ref: `Ticket`, `User`. Unique per `(ticket, user)` |
| **TicketStatusHistory** | `ticket_status_history` | Precise elapsed time logs of status transitions. | `from_status`, `to_status`, `duration_seconds`, `status` | Ref: `Ticket`, `User` (changed_by) |

---

## ⚙️ Domain Services & Business Logic Hooks (`backend_django/tickets/services.py`)

1. **`TicketService` (`@register_service("ticket")`)**:
   - `before_create`:
     - Auto-generates sequential ticket keys (`TCK-1`, `TCK-2`, etc.).
     - Defaults `ticket_status = "Open"`, `priority = "Medium"`, `meta_status = "active"`.
     - Sets `created_by = context.user`.
   - `after_create`:
     - Automatically registers creator as `TicketParticipant(role="creator")`.
     - Automatically registers assignee as `TicketParticipant(role="assignee")`.
     - Records initial audit log in `TicketActivityLog(action="created")`.
     - Records initial status in `TicketStatusHistory(to_status="Open")`.
     - Side effects via `transaction.on_commit`:
       - Dispatches push notification to assignee.
       - Back-links to `Task` if `linked_task` was attached on creation (`task.linkedTicketId = ticket`).
   - `before_update`:
     - Stamps `resolved_at = now()` when transitioning to `"Resolved"`.
     - Stamps `closed_at = now()` when transitioning to `"Closed"`.
   - `after_update`:
     - Computes duration in seconds spent in previous status and appends to `TicketStatusHistory`.
     - Records `TicketActivityLog(action="status_changed")` and `action="assigned"`.
     - Enrolls new assignee in `TicketParticipant`.
     - Side effects via `transaction.on_commit`:
       - Dispatches update notifications to all watchers and participants.
       - **Bi-Directional Task Sync**: If ticket is `"Resolved"` or `"Closed"`, automatically transitions linked `Task.status` to `"Done"` and sets `progress = 100`.

2. **`TicketCommentService` (`@register_service("ticket_comment")`)**:
   - `before_create`:
     - Validates non-empty content and binds `author = context.user`.
   - `after_create`:
     - Registers commenter as `TicketParticipant(role="watcher")`.
     - Records `TicketActivityLog(action="comment_added")`.
     - **Dynamic Status Switching**:
       - When internal staff posts a public comment, automatically transitions parent ticket status to `"Waiting For Customer"`.
       - When a customer replies, transitions parent ticket status to `"In Progress"`.
     - Side effects via `transaction.on_commit`:
       - Notifies participants (respecting `is_internal` visibility for non-staff).

3. **`TicketAttachmentService` (`@register_service("ticket_attachment")`)**:
   - Records `TicketActivityLog(action="attachment_uploaded")`.

---

## 📡 Dynamic API Usage (Populate Pipeline)

- **Create Support Ticket**:
  ```http
  POST /api/populate/create/ticket/
  Content-Type: application/json

  {
    "title": "Payment Gateway Webhook Timeout",
    "description": "Webhook callbacks are taking over 5000ms.",
    "client": 1,
    "project_type": 1,
    "priority": "Urgent"
  }
  ```
- **Post Discussion Comment**:
  ```http
  POST /api/populate/create/ticket_comment/
  Content-Type: application/json

  {
    "ticket": 1,
    "content": "Please test on staging.",
    "is_internal": false
  }
  ```
- **Read Ticket with Deep Population**:
  ```http
  POST /api/populate/read/ticket/
  Content-Type: application/json

  {
    "filter": { "ticket_status": "In Progress" },
    "populateFields": {
      "client": "name",
      "project_type": "name",
      "assignee": "username,email",
      "linked_task": "task_key,title,status"
    }
  }
  ```

---

## 🚀 Database Indexes (MySQL Engine)
- `tickets`:
  - `(status, ticket_status, client_id)`
  - `(status, assignee_id, priority)`
  - `(status, meta_status, created_at)`
- `ticket_comments`:
  - `(status, ticket_id, created_at)`
- `ticket_activity_logs`:
  - `(status, ticket_id, created_at)`
  - `(status, action)`
- `ticket_participants`:
  - `(status, ticket_id, role)`
  - `(status, user_id)`
  - Unique constraint on `(ticket_id, user_id)`
- `ticket_status_history`:
  - `(status, ticket_id, created_at)`
