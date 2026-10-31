# Module Brain: Recruitment & Employee Onboarding

> **Domain:** Job Openings, Applicant Tracking (ATS), Candidate Pipeline, Onboarding Checklists, and Verification.  
> **App Location:** `backend_django/recruitment/`  
> **Tables:** `recruitment_job_categories`, `recruitment_job_types`, `recruitment_job_openings`, `recruitment_candidates`, `recruitment_onboarding_templates`, `recruitment_onboardings`.

---

## 1. Domain Overview & Principles

The Recruitment suite governs hiring and employee transition lifecycles:
1. **Job Categories & Types (`JobCategory`, `JobType`)**: Classifications for activities, billing rates, productivity benchmarks, and stage derivations.
2. **Job Opening (`JobOpening`)**: Vacancy postings with department/designation mapping, target openings, public career board visibility, and filled counters.
3. **Candidate (`Candidate`)**: Applicant tracking system (ATS) with sequential application numbers (`APP-YYYY-XXXX`), resume storage, interview logs, offer details, and pipeline stages (`Applied` &rarr; `Screening` &rarr; `Interview` &rarr; `Offered` &rarr; `Hired` / `Rejected`).
4. **Onboarding Template (`OnboardingTemplate`)**: Reusable onboarding blueprints organized by department, designation, and employment type.
5. **Onboarding Tracker (`Onboarding`)**: Post-hire transition tracking with dynamic percentage completion calculation, document upload/verification flags, and SLA monitoring.

---

## 2. Backend Models

| Model | Table | Direct Mutations | Key Fields |
|---|---|---|---|
| `JobCategory` | `recruitment_job_categories` | Admin Standard | `name`, `icon`, `color`, `order`, `is_billable`, `is_active` |
| `JobType` | `recruitment_job_types` | Admin Standard | `name`, `category`, `default_hourly_rate`, `expected_productivity`, `required_skill_level`, `is_active` |
| `JobOpening` | `recruitment_job_openings` | Standard (Public Read) | `title`, `department`, `designation`, `openings`, `filled`, `status`, `published_at`, `closed_at` |
| `Candidate` | `recruitment_candidates` | Standard (Public Apply) | `first_name`, `last_name`, `email`, `application_id`, `job_opening`, `stage`, `interview_rating`, `offered_salary`, `joining_date` |
| `OnboardingTemplate` | `recruitment_onboarding_templates` | Standard | `title`, `department`, `designation`, `employment_type`, `checklist`, `is_active`, `is_default` |
| `Onboarding` | `recruitment_onboardings` | Standard | `employee`, `candidate`, `joining_date`, `checklist`, `completion_percent`, `verified_percent`, `status`, `sla_breached` |

---

## 3. Services & Hook Lifecycles

### JobOpeningService (`@register_service("job_opening")`)
- **Public Visibility**: Unauthenticated users and employees without HR capability only see vacancies with `status="Published"`.
- **Publication Lifecycle**: Automatically sets `published_at` when published, and `closed_at` when closed or filled.

### CandidateService (`@register_service("candidate")`)
- **`before_create`**: Auto-generates sequential application ID (`APP-YYYY-XXXX`).
- **`before_update`**:
  - Automatically records stage changes in `stage_history`.
  - When candidate is marked `Hired`, increments `job_opening.filled` and transitions the job opening to `Filled` if quota is met.

### OnboardingService (`@register_service("onboarding")`)
- **Template Auto-Population**: When an onboarding record is created with an empty checklist, automatically pulls and computes due dates from the matching `OnboardingTemplate`.
- **Real-Time Progress Derivation**: On every checklist update, computes `completion_percent` and `verified_percent`. When both reach 100%, transitions status to `Completed`.

