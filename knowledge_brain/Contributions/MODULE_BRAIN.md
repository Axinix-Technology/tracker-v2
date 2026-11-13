# Work Contributions & Shareholder Equity Subsystem

> **App Location**: `backend/contributions/`  
> **Frontend Pages**: `Frontend/src/pages/contributions/` (`dashboard.jsx`, `add.jsx`, `follow-ups.jsx`, `reports.jsx`)  
> **Frontend Components**: `Frontend/src/components/Contributions/`  
> **Status**: Production Ready  
> **Target Branch**: `feat/work-status-update`

---

## 1. Module Purpose & Core Value

The **Work Contributions & Shareholder Equity Subsystem** translates unstructured daily team member activity logs (such as WhatsApp, Slack, or chat updates) into mathematically verified, auditable contribution points. These points directly drive the **Shareholder Profit Share %** allocations and dividend distributions.

---

## 2. Mathematical Point Weighting & Formulas

### 2.1 The Two Contribution Scopes
* **Project Contribution**: Client-billable deliverables and systems (e.g. *Sri KaliGuhan Clothing*, *Tea Shop*).
* **Company Contribution**: Strategic internal IP, reusable systems, architecture, and DevOps infrastructure (e.g. *Axinix Technologies*, *populate_core*, *AR.I.S*).

### 2.2 The 6 Evaluation Factors ($100\%$ Total Weight)
$$\Phi = \sum_{F_i = \text{TRUE}} W_i$$

1. **Effort & Responsibility ($20\%$)**: Genuine consistency, time spent, unprompted initiative.
2. **Complexity & Skill ($15\%$)**: Technical difficulty, specialist knowledge, independence.
3. **Deliverable & Completion ($25\%$)**: Working milestone, live deployment, client acceptance. *(If FALSE, capped at $75\%$ and enters In-Progress Follow-Up lifecycle)*.
4. **Quality & Reliability ($20\%$)**: Clean architectural compliance, no regressions, passing tests.
5. **Evidence & Ownership ($10\%$)**: Verifiable commit hash, PR link, client confirmation.
6. **Outcome & Long-Term Value ($10\%$)**: Reusable company asset, revenue expansion, lasting value.

### 2.3 Mathematical Formulas
$$P_{\text{base}} = \text{Worked Days} \times \text{Base Points per Day}$$
$$P_{\text{final}} = P_{\text{base}} \times \left( \frac{\Phi}{100.0} \right)$$
$$\text{Shareholder Profit Share \%} = \left( \frac{\sum P_{\text{final}}^{\text{member}}}{\sum P_{\text{final}}^{\text{total}}} \right) \times 100$$

---

## 3. Database Models & Populate Engine Registration

1. **`ContributionCategory`** (Master):
   * Registered with `register_model("contribution_category", table_type="master")`.
   * Stores 58+ categories with defined `base_points` (e.g. Reusable System Architecture = 12, Development = 10, Bug Fixing = 8).
2. **`ContributionFactor`** (Master):
   * Registered with `register_model("contribution_factor", table_type="master")`.
   * Stores the 6 weighted criteria ($20\%, 15\%, 25\%, 20\%, 10\%, 10\%$).
3. **`WorkContribution`** (Transaction / Ledger):
   * Registered with `register_model("work_contribution", table_type="transaction", status_field="lifecycle_status")`.
   * Implements the In-Progress Follow-Up state machine: `delivery_status` (`completed`, `in_progress`, `stalled`, `on_hold`).
   * Evaluates and freezes `factor_percentage` and `final_points` via `WorkContributionService` hooks to prevent client tampering.

---

## 4. In-Progress Follow-Up Lifecycle Engine

* Any activity where **Deliverable & Completion** is `FALSE` is automatically tagged `in_progress` with points temporarily calculated at $75\%$.
* If no completion update arrives after $48$ hours, the item is tagged **Stalled** on `/contributions/follow-ups`.
* When the employee or lead marks the item completed, the remaining $25\%$ deliverable weight is unlocked and credited.

---

## 5. Multipage Frontend Routing (`Frontend/src/pages/contributions/`)

Adhering strictly to **Sacred Law 8** (pure page-only routing):
* `/contributions/dashboard`: Executive KPIs, 3-way comparative matrix, visual equity bar gauge, and profit pool simulator.
* `/contributions/add`: WhatsApp-style quick status drop with AI extraction and live calibration cards.
* `/contributions/follow-ups`: In-progress and stalled tasks radar with direct completion resolvers.
* `/contributions/reports`: Multi-dimensional filters (date range, member, scope, client, category, status), dynamic aggregate strip, granular data table, and single entry detail drawer.



---

## 7. Navigation Integration & Tenant User Session Resolution

### 7.1 Dynamic User Navigation
* Navigation hierarchy is constructed via `backend/users/navigation.py` using `scripts/playground/sidebar.json` and injecting `CONTRIBUTIONS_NAV` at position 1.
* Gated by dynamic multi-tenant policy: only modules present in `tenant.enabled_modules` (or unlocked for `SuperAdmin`) are served to `/api/auth/me/context`.
* Top-level and child routes:
  1. **Equity & Profit Share**: `/contributions/dashboard`
  2. **Add Work Status**: `/contributions/add`
  3. **Follow-Up Radar**: `/contributions/follow-ups`
  4. **Contribution Reports**: `/contributions/reports`

### 7.2 Session Identity Resolution
* `backend/users/views.py` (`LoginView`, `UserContextView`) dynamically sets `name`, `tenantId`, and `tenantSlug` in JWT payload and user data.
* Frontend `TopNavBar.jsx` and `useUserProfile.js` consume `name || firstName` ensuring immediate, authenticated display of user identity without fallback to `"Guest"`.
