# Module Brain — Notifications & Event Dispatch

## 1. Architectural Overview
- **Models**:
  - `Notification` (registered as `notification`, aliases: `notifications`)
  - `NotificationReceptionist` (registered as `notification_receptionist`, aliases: `notification_receptionists`)
- **Services**:
  - `NotificationService` in [`notifications/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/notifications/services.py)
  - `NotificationReceptionistService` in [`notifications/services.py`](file:///d:/Axinix%20Projects/tracker-v2/backend_django/notifications/services.py)

---

## 2. Security & Scoping Rules
- **Row-Level Recipient Isolation**:
  - `before_read` and `get_policy_scope` apply `Q(recipient=context.user)` unless `context.is_superadmin` is True.
  - Guarantees that employees only receive their own notifications, preventing organization-wide data leakage.
- **Anti-Spoofing Sender Binding**:
  - `before_create` ignores any client-supplied `sender` payload and forces `sender_id = context.user.id`.
- **Ownership Verification on Updates**:
  - `before_update` ensures users can only mutate notifications where `instance.recipient == context.user`.
  - Non-owner update attempts return 404 (due to row-level scoping) or 403 Forbidden.
