"""
Seed Canonical Workhub ERP Modules into Control Plane
=====================================================
Single source of truth: populates the 10 core modules with their model collections,
human-readable descriptions, categories, icons, pricing, features, and prerequisites.
POST /api/populate/read/module
"""

from decimal import Decimal
from django.core.management.base import BaseCommand
from control_plane.models import Module
from control_plane.registry import CLIENT_BUSINESS_MODULES

WORKHUB_MODULES = [
    {
        "module_id": "attendance",
        "name": "Attendance & Geofencing",
        "category": "Workforce & HR",
        "icon": "Clock",
        "price_per_user_monthly": Decimal("25.00"),
        "description": "Biometric hardware sync, mobile geofenced selfie punch, flexible shift rosters, overtime computation, and multi-tier leave approval workflows.",
        "features": [
            "Biometric hardware & cloud fingerprint sync",
            "Geofenced mobile punch with live selfie verification",
            "Shift roster scheduling & rotational shifts",
            "Overtime calculation & compensatory off requests",
            "Multi-tier leave application & approval chains",
            "Statutory holiday calendars & custom overrides",
        ],
        "prerequisites": [],
        "collections": list(CLIENT_BUSINESS_MODULES.get("attendance", [])),
    },
    {
        "module_id": "payroll",
        "name": "Payroll & Tax Compliance",
        "category": "Finance & HR",
        "icon": "DollarSign",
        "price_per_user_monthly": Decimal("40.00"),
        "description": "One-click automated salary calculation, statutory compliance (PF, ESI, TDS, PT), customizable salary structures, reimbursement claims, and encrypted PDF payslips.",
        "features": [
            "One-click automated monthly payroll calculation",
            "Statutory PF, ESI, TDS, and Professional Tax compliance",
            "Flexible earnings and deductions salary structures",
            "Expense reimbursement claims with receipt upload",
            "Password-protected encrypted PDF payslip generation",
            "Direct bank disbursement salary text/excel file export",
        ],
        "prerequisites": ["attendance"],
        "collections": list(CLIENT_BUSINESS_MODULES.get("payroll", [])),
    },
    {
        "module_id": "tasks",
        "name": "Tasks & Project Sprints",
        "category": "Operations",
        "icon": "CheckSquare",
        "price_per_user_monthly": Decimal("30.00"),
        "description": "Agile Kanban boards, multi-assignee task distribution, milestone tracking, immutable ticket snapshots, daily work logs, and team velocity metrics.",
        "features": [
            "Interactive Kanban & list views with drag-and-drop",
            "Milestones, sprint cycles, and deadline alerts",
            "Self-contained ticket snapshots for cross-module integrity",
            "Time tracking and daily activity work logs",
            "Subtasks, checklist items, and file attachments",
            "Custom priority matrix (Critical, High, Medium, Low)",
        ],
        "prerequisites": [],
        "collections": list(CLIENT_BUSINESS_MODULES.get("tasks", [])),
    },
    {
        "module_id": "tickets",
        "name": "Support & Service Desk",
        "category": "Customer Experience",
        "icon": "Headphones",
        "price_per_user_monthly": Decimal("35.00"),
        "description": "Multi-agent ticketing queue, dynamic SLA escalation timers, priority routing, customer communication trails, and cross-module task linking.",
        "features": [
            "Multi-agent shared ticketing inbox & assignment",
            "Configurable SLA timers with automated escalation alerts",
            "Priority queues (Urgent, High, Normal, Low)",
            "Convert customer tickets directly into operational tasks",
            "Customer satisfaction (CSAT) ratings and audit history",
            "Private internal notes vs. public customer responses",
        ],
        "prerequisites": [],
        "collections": list(CLIENT_BUSINESS_MODULES.get("tickets", [])),
    },
    {
        "module_id": "crm",
        "name": "CRM & Sales Opportunity Pipeline",
        "category": "Sales & Growth",
        "icon": "TrendingUp",
        "price_per_user_monthly": Decimal("45.00"),
        "description": "Lead capture and scoring, visual multi-stage deal pipelines, follow-up scheduling, omnichannel customer communication, and sales velocity reporting.",
        "features": [
            "Visual drag-and-drop deal pipeline with customizable stages",
            "Lead capture, automatic qualification, and rep routing",
            "Omnichannel contact timeline (Email, Phone, WhatsApp logs)",
            "Automated follow-up reminders and scheduled meetings",
            "Sales forecasting and win/loss conversion analytics",
            "Instant conversion of won opportunities into billing quotations",
        ],
        "prerequisites": [],
        "collections": list(CLIENT_BUSINESS_MODULES.get("crm", [])),
    },
    {
        "module_id": "billing",
        "name": "Billing & GST Invoicing",
        "category": "Finance & HR",
        "icon": "Receipt",
        "price_per_user_monthly": Decimal("40.00"),
        "description": "Automated GST/tax invoicing, proforma quotations, order acknowledgments, payment gateway integration, credit notes, and real-time financial ledgers.",
        "features": [
            "GST tax invoices with HSN/SAC code lookup",
            "Proforma invoices, quotes, and Order Acknowledgments (OA)",
            "Razorpay/Stripe integrated payment links and auto-receipts",
            "Credit notes, debit adjustments, and client advance ledgers",
            "Automated overdue payment reminders via WhatsApp/Email",
            "Export ledgers for Tally / Zoho Books / CA audit",
        ],
        "prerequisites": [],
        "collections": list(CLIENT_BUSINESS_MODULES.get("billing", [])),
    },
    {
        "module_id": "assets",
        "name": "Enterprise Asset Management",
        "category": "Operations",
        "icon": "Box",
        "price_per_user_monthly": Decimal("25.00"),
        "description": "Physical asset procurement, QR barcode tagging, hardware allocation, depreciation calculation, maintenance schedules, and disposal audit logs.",
        "features": [
            "Hardware and physical inventory asset registry",
            "Unique QR code and barcode sticker generation",
            "Employee asset check-out and return audit trail",
            "Automated straight-line & WDV depreciation computation",
            "Vendor warranty tracking and scheduled AMC maintenance",
            "Scrap and asset write-off authorization workflows",
        ],
        "prerequisites": [],
        "collections": list(CLIENT_BUSINESS_MODULES.get("assets", [])),
    },
    {
        "module_id": "recruitment",
        "name": "Recruitment & Applicant Tracking",
        "category": "Workforce & HR",
        "icon": "UserPlus",
        "price_per_user_monthly": Decimal("30.00"),
        "description": "Job requisition workflows, applicant pipeline management, interview scoring rubrics, offer letter generation, and digital candidate onboarding.",
        "features": [
            "Public career portal job postings and applicant capture",
            "Kanban pipeline: Sourced -> Screening -> Interview -> Offer",
            "Standardized interviewer scorecards and evaluation rubrics",
            "Automated offer letter generation with e-signature support",
            "1-Click candidate conversion into permanent employee record",
            "Candidate document collection checklist before Day 1",
        ],
        "prerequisites": ["hr"],
        "collections": list(CLIENT_BUSINESS_MODULES.get("recruitment", [])),
    },
    {
        "module_id": "hr",
        "name": "HRMS & Employee Records",
        "category": "Workforce & HR",
        "icon": "Users",
        "price_per_user_monthly": Decimal("20.00"),
        "description": "Comprehensive employee digital dossiers, document vault, organizational hierarchy charts, lifecycle promotion history, and company policy distribution.",
        "features": [
            "Centralized employee master database and digital dossiers",
            "Document vault with expiry tracking (IDs, contracts, certs)",
            "Interactive visual department hierarchy org chart",
            "Employee lifecycle events: promotions, transfers, increments",
            "Company handbook distribution with read-acknowledgment",
            "Self-service employee profile update requests",
        ],
        "prerequisites": [],
        "collections": list(CLIENT_BUSINESS_MODULES.get("hr", [])),
    },
    {
        "module_id": "feed",
        "name": "Internal Feed & Team Channels",
        "category": "Operations",
        "icon": "MessageSquare",
        "price_per_user_monthly": Decimal("15.00"),
        "description": "Enterprise social feed, department announcements, real-time team messaging channels, pinned notifications, and cross-office communication.",
        "features": [
            "Company-wide announcement broadcast feed with comments",
            "Departmental discussion channels and pinned notices",
            "Employee recognition badges, birthdays, and work anniversaries",
            "Mobile push notifications for critical enterprise alerts",
            "Rich media sharing (images, policy PDFs, project links)",
            "Moderation controls and read receipts for leadership",
        ],
        "prerequisites": [],
        "collections": list(CLIENT_BUSINESS_MODULES.get("feed", [])),
    },
]


class Command(BaseCommand):
    help = "Seeds the 10 canonical Workhub ERP modules into control_plane_modules with single-source-of-truth metadata"

    def handle(self, *args, **options):
        self.stdout.write("Seeding canonical Workhub ERP modules into MySQL...")
        for item in WORKHUB_MODULES:
            mod, _ = Module.objects.update_or_create(
                module_id=item["module_id"],
                defaults={
                    "name": item["name"],
                    "category": item["category"],
                    "icon": item["icon"],
                    "price_per_user_monthly": item["price_per_user_monthly"],
                    "description": item["description"],
                    "features": item["features"],
                    "prerequisites": item["prerequisites"],
                    "collections": item["collections"],
                    "is_active": True,
                    "lifecycle_status": 1,
                }
            )
            self.stdout.write(f"  ✓ Synced: {mod.name} [₹{mod.price_per_user_monthly}/mo]")

        self.stdout.write(self.style.SUCCESS("All 10 modules synchronized into single source of truth!"))
