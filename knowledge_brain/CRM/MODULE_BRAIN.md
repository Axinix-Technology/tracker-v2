# CRM Module Brain

> **Domain:** Customer Relationship Management, Leads, Contacts, Opportunities, Activities, and Meetings.  
> **App Location:** `backend_django/crm/`  
> **Tables:** `crm_lead_types`, `crm_reference_types`, `crm_contacts`, `crm_opportunities`, `crm_activities`, `crm_meetings`.

---

## 1. Domain Overview & Principles

The CRM suite manages pre-sales prospecting, account conversions, deal pipelines, and client engagement:
1. **Lead Types & Reference Types (`LeadType`, `ReferenceType`)**: Master classifications for lead channels and business references.
2. **Contact (`Contact`)**: Prospect/lead ledger tracking contact info, interaction history, assigned representatives, and conversion to clients (`users_clients`).
3. **Opportunity (`Opportunity`)**: Pipeline deal tracker evaluating stage progression (`New` &rarr; `Discovery` &rarr; `Proposal` &rarr; `Negotiation` &rarr; `Won`/`Lost`), revenue forecasting, win probability, and linking to quotations (`billing_quotations`) and contracts (`billing_order_acknowledgements`).
4. **CRM Activity (`CRMActivity`)**: Chronological audit trail of customer interactions (calls, emails, notes, tasks).
5. **CRM Meeting (`CRMMeeting`)**: Calendar scheduling with actual start/end tracking, attendee lists, location, and meeting outcome notes.

---

## 2. Backend Models

| Model | Table | Direct Mutations | Key Fields |
|---|---|---|---|
| `LeadType` | `crm_lead_types` | Admin Standard | `name`, `description`, `status` |
| `ReferenceType` | `crm_reference_types` | Admin Standard | `name`, `description`, `status` |
| `Contact` | `crm_contacts` | Standard | `first_name`, `last_name`, `company_name`, `email`, `phone`, `assigned_to`, `status`, `contact_history`, `converted_client` |
| `Opportunity` | `crm_opportunities` | Standard | `account`, `contact`, `name`, `owner`, `stage`, `expected_value`, `probability`, `expected_close_date`, `quotation`, `contract` |
| `CRMActivity` | `crm_activities` | Standard | `client`, `type`, `content`, `performed_by`, `timestamp` |
| `CRMMeeting` | `crm_meetings` | Standard | `client`, `title`, `scheduled_time`, `end_time`, `actual_start_time`, `actual_end_time`, `status`, `outcome`, `attendees` |

---

## 3. Services & Hook Lifecycles

### ContactService (`@register_service("contact")`)
- **`get_policy_scope`**: Sales representatives see leads assigned to them or contacted by them. Managers with `contact.read` capability query company-wide leads.
- **`before_update`**:
  - Automatically appends `new_contact_log` to `contact_history`, updating `contacted_by` and `contacted_at`.
  - When marked `Converted`, automatically creates a new `Client` in `users_clients` if unlinked.

### OpportunityService (`@register_service("opportunity")`)
- **Pipeline Stage Automations**:
  - `New` (10%) &rarr; `Discovery` (20%) &rarr; `Proposal` (50%) &rarr; `Negotiation` (80%) &rarr; `Won` (100%) or `Lost` (0%).
  - Automatically sets `actual_close_date` upon terminal states (`Won`, `Lost`).
  - Enforces mandatory `lost_reason` on `Lost` deals.

### CRMMeetingService (`@register_service("crm_meeting")`)
- **Calendar & Timeline Integrity**:
  - Enforces `scheduled_time < end_time`.
  - Captures `actual_start_time` and `actual_end_time` upon status transitions (`Started`, `Completed`).
