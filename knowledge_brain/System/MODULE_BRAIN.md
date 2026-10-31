# Module Brain: System Telemetry & Platform Configuration

> **Domain:** Status Master, Cross-Model State Mappings, Outbound SMTP Config, Release Notes, Canonical Resources, and Multi-Step Workflows.  
> **App Location:** `backend_django/system/`  
> **Tables:** `system_status_configs`, `system_status_mappings`, `system_email_configs`, `system_service_providers`, `system_release_notes`, `system_resources`, `system_workflows`, `system_products`.

---

## 1. Domain Overview & Principles

The System module serves as the platform configuration bedrock:
1. **Status Configuration (`StatusConfig`)**: Model-level state definitions, hex color mappings, and terminal/sequential indicators.
2. **Status Mapping (`StatusMapping`)**: Declarative state synchronization linking paired entities (e.g., tasks & tickets).
3. **Email Configuration (`EmailConfig`)**: Outbound SMTP credential management with mandatory password redaction in API responses (`get_forbidden_fields`).
4. **Service Provider (`ServiceProvider`)**: External third-party contractor and vendor registry with GST/PAN/banking metadata.
5. **Release Note (`ReleaseNote`)**: Version release announcements, categorized changelogs (features, fixes, security), and user read acknowledgment tracking (`seen_by`).
6. **Resource (`Resource`)**: Single source of truth decoupling UI `can()` capability keys from backend model names.
7. **Workflow (`Workflow`)**: Declarative approval, escalation, and onboarding multi-step execution graphs.
8. **Product (`Product`)**: Commercial catalog items referenced in quotations and invoices.

---

## 2. Backend Models

| Model | Table | Key Fields |
|---|---|---|
| `StatusConfig` | `system_status_configs` | `model_name`, `label`, `meta_statuses`, `workflow_statuses` |
| `StatusMapping` | `system_status_mappings` | `source_model`, `target_model`, `link_field`, `reverse_link_field`, `mappings`, `is_active` |
| `EmailConfig` | `system_email_configs` | `service`, `host`, `port`, `secure`, `username`, `password` (masked), `from_name`, `from_email`, `enabled` |
| `ServiceProvider` | `system_service_providers` | `name`, `contact_person`, `email`, `phone`, `gst_in`, `pan_number`, `bank_details`, `services`, `status` |
| `ReleaseNote` | `system_release_notes` | `version`, `release_date`, `title`, `tagline`, `is_latest`, `is_published`, `categories`, `seen_by` |
| `Resource` | `system_resources` | `key`, `model_name`, `display_name`, `module`, `description`, `is_active` |
| `Workflow` | `system_workflows` | `name`, `model_name`, `trigger_type`, `conditions`, `steps`, `is_active` |
| `Product` | `system_products` | `name`, `code`, `description`, `category`, `unit_price`, `tax_rate`, `is_active` |

