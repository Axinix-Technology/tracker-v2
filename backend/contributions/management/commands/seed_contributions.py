import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from contributions.models import ContributionCategory, ContributionFactor, WorkContribution

User = get_user_model()

FACTORS = [
    {
        "code": "effort",
        "name": "Effort & Responsibility",
        "weight": 0.20,
        "criteria": "Genuine effort, responsibility, consistency, and time spent on meaningful work",
        "sort_order": 1,
    },
    {
        "code": "complexity",
        "name": "Complexity & Skill",
        "weight": 0.15,
        "criteria": "Difficulty, specialist knowledge, problem-solving, and independence",
        "sort_order": 2,
    },
    {
        "code": "deliverable",
        "name": "Deliverable & Completion",
        "weight": 0.25,
        "criteria": "Completed outputs, qualified opportunities, implemented systems, and agreed milestones",
        "sort_order": 3,
    },
    {
        "code": "quality",
        "name": "Quality & Reliability",
        "weight": 0.20,
        "criteria": "Quality of execution, correctness, professionalism, reliability, and sustainability",
        "sort_order": 4,
    },
    {
        "code": "evidence",
        "name": "Evidence & Ownership",
        "weight": 0.10,
        "criteria": "Verifiable records, follow-ups, ownership, accountability, and documented progress",
        "sort_order": 5,
    },
    {
        "code": "outcome",
        "name": "Outcome & Long-Term Value",
        "weight": 0.10,
        "criteria": "Revenue potential, customer value, reusable assets, productivity, risk reduction, and lasting company benefits",
        "sort_order": 6,
    },
]

PROJECT_CATEGORIES = [
    ("Technical Architecture", 12.0, "Designing system structure or technical solutions"),
    ("Development", 10.0, "Implementing a feature or API"),
    ("Technical Guidance", 8.0, "Guiding a developer through implementation"),
    ("Bug Fixing", 8.0, "Diagnosing and resolving defects"),
    ("Deployment & Server Maintenance", 8.0, "Deployment, monitoring, troubleshooting"),
    ("Requirements Analysis", 8.0, "Understanding client requirements and documenting specifications"),
    ("Independent Testing", 7.0, "Designing and executing tests independently"),
    ("Project Management", 7.0, "Planning, assigning tasks, tracking delivery"),
    ("Quality Assurance", 7.0, "Release verification and regression checks"),
    ("Code Review", 6.0, "Reviewing code and identifying defects"),
    ("Guided Bug Fixing", 5.0, "Fixing bugs pointed out by Testing"),
    ("Guided Testing", 5.0, "Testing under developer guidance"),
    ("Client Communication", 5.0, "Requirement clarification, demonstrations, support coordination"),
    ("Research & Investigation", 5.0, "Investigating technical problems or evaluating solutions"),
    ("Mentoring & Knowledge Sharing", 5.0, "Training teammates and transferring knowledge"),
    ("Documentation", 4.0, "Technical documentation and user guides"),
    ("Competitor Analysis & UI/UX Benchmarking", 7.0, "Researching competitor interfaces, features, integrations, and user experience"),
    ("Technical Feasibility & Solution Evaluation", 8.0, "Evaluating technical feasibility, implementation effort, dependencies, and risks"),
    ("Product Gap Analysis & Feature Recommendations", 7.0, "Identifying missing features and recommending improvements for the project"),
    ("Client Implementation & Onboarding", 8.0, "Helping clients configure and start using the system"),
    ("Client Training & Knowledge Transfer", 6.0, "Training clients on product inward, stock maintenance, billing, and reports"),
    ("Client Business Operations Support", 7.0, "Assisting with stock inward, stock maintenance, and agreed operational processes"),
    ("Client Relationship & Account Management", 7.0, "Maintaining client relationships, conducting business follow-ups, and coordinating concerns"),
    ("Client Marketing & Product Content Support", 6.0, "Photographing products, preparing product information, and sharing materials with the marketing team"),
    ("Customer Success & Adoption", 7.0, "Helping clients use the system effectively and addressing adoption problems"),
    ("Business Process Analysis & Improvement", 7.0, "Understanding client workflows and recommending operational improvements"),
    ("Data Preparation & Product Catalog Management", 5.0, "Creating product entries, organising images, and validating product information"),
    ("Project Coordination & Stakeholder Follow-up", 6.0, "Coordinating requests, following up on pending work, and arranging activities"),
    ("Knowledge Acquisition & Technology Learning", 4.0, "Learning a relevant technology or business process to support project work"),
]

COMPANY_CATEGORIES = [
    ("Business Strategy & Planning", 12.0, "Company roadmap, product strategy, business planning"),
    ("Client Acquisition", 12.0, "Converting prospects into paying clients"),
    ("Reusable System Architecture", 12.0, "Designing architecture shared across multiple products"),
    ("Business Development", 10.0, "Identifying potential clients, developing sales opportunities"),
    ("DevOps & CI/CD Infrastructure", 10.0, "Creating reusable CI/CD pipelines for company applications"),
    ("Cloud Infrastructure & Security", 10.0, "Shared AWS architecture, access controls, security hardening"),
    ("Reusable Component Development", 10.0, "Shared libraries, APIs, common modules, reusable services"),
    ("Internal Tool Development", 9.0, "Building tools that improve internal operations"),
    ("Product Research & Innovation", 8.0, "Researching new products, technologies, and opportunities"),
    ("Company-Wide Technical Guidance", 8.0, "Guiding developers across multiple projects"),
    ("Automation & Productivity Improvements", 8.0, "Automating repetitive tasks across projects"),
    ("Financial & Commercial Planning", 8.0, "Pricing models, project cost estimates, financial planning"),
    ("Technical Feasibility & Technology Evaluation", 8.0, "Evaluating technologies and integrations for potential company products"),
    ("Product Gap Analysis & Roadmap Recommendations", 8.0, "Identifying company-wide product gaps and prioritising future improvements"),
    ("Technical Standards & Best Practices", 7.0, "Coding standards, architecture guidelines, engineering processes"),
    ("Recruitment & Team Development", 7.0, "Technical interviews, onboarding, team training"),
    ("Marketing & Brand Development", 7.0, "Company website, case studies, technical content, marketing assets"),
    ("Sales Proposals & Demonstrations", 7.0, "Preparing proposals, demonstrations, estimates, and presentations"),
    ("Partnership & Vendor Development", 7.0, "Establishing useful business relationships and vendor partnerships"),
    ("Competitor Analysis & Market Intelligence", 7.0, "Researching competitors' websites, features, UI/UX, integrations, pricing, and market positioning"),
    ("Client Success & Retention Support", 7.0, "Supporting customer satisfaction, adoption, retention, and expansion opportunities"),
    ("Internal Process Improvement", 7.0, "Improving company workflows, reporting, coordination, and operating procedures"),
    ("Business Process & Industry Research", 7.0, "Studying industry workflows, customer needs, and opportunities for new services"),
    ("Strategic Partnership Development", 7.0, "Developing relationships that create meaningful long-term business opportunities"),
    ("Company Documentation", 6.0, "Development standards, deployment guides, internal technical knowledge base"),
    ("Company Operations & Administration", 6.0, "Internal processes, resource planning, operational coordination"),
    ("Product Documentation for Future Use", 6.0, "Reusable product manuals, implementation guides, technical specifications"),
    ("Research Documentation & Implementation Planning", 6.0, "Creating actionable research reports, technical specifications, estimates, and implementation plans"),
    ("Marketing Operations & Content Production", 6.0, "Preparing product photographs, promotional content, and marketing materials for company use"),
]

TEAM_MEMBERS = [
    {"username": "arunbharathi", "first_name": "Arunbharathi", "email": "arunbharathi@axinix.com"},
    {"username": "ajay", "first_name": "Ajay", "email": "ajay@axinix.com"},
    {"username": "siva", "first_name": "Siva Anna", "email": "siva@axinix.com"},
    {"username": "rithika", "first_name": "Rithika", "email": "rithika@axinix.com"},
    {"username": "karuppasamy", "first_name": "Karuppasamy", "email": "karuppasamy@axinix.com"},
    {"username": "ruthran", "first_name": "Ruthran", "email": "ruthran@axinix.com"},
    {"username": "guruprasath", "first_name": "Guruprasath", "email": "guruprasath@axinix.com"},
    {"username": "boopalan", "first_name": "Boopalan", "email": "boopalan@axinix.com"},
]


class Command(BaseCommand):
    help = "Seed contribution factors, categories, team members, and initial company contributions"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("===> Seeding Contribution Factors..."))
        for f in FACTORS:
            ContributionFactor.objects.update_or_create(
                code=f["code"],
                defaults={
                    "name": f["name"],
                    "weight": f["weight"],
                    "criteria": f["criteria"],
                    "sort_order": f["sort_order"],
                    "status": 1,
                    "is_active": True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(FACTORS)} evaluation factors."))

        self.stdout.write(self.style.NOTICE("===> Seeding Categories..."))
        cat_count = 0
        for name, points, desc in PROJECT_CATEGORIES:
            ContributionCategory.objects.update_or_create(
                name=name,
                scope="Project Contribution",
                defaults={
                    "base_points": points,
                    "description": desc,
                    "status": 1,
                    "is_active": True,
                }
            )
            cat_count += 1

        for name, points, desc in COMPANY_CATEGORIES:
            ContributionCategory.objects.update_or_create(
                name=name,
                scope="Company Contribution",
                defaults={
                    "base_points": points,
                    "description": desc,
                    "status": 1,
                    "is_active": True,
                }
            )
            cat_count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {cat_count} contribution categories."))

        self.stdout.write(self.style.NOTICE("===> Ensuring Team Members exist..."))
        user_map = {}
        for tm in TEAM_MEMBERS:
            u, _ = User.objects.get_or_create(
                username=tm["username"],
                defaults={
                    "first_name": tm["first_name"],
                    "email": tm["email"],
                    "is_active": True,
                }
            )
            if not u.first_name:
                u.first_name = tm["first_name"]
                u.save(update_fields=["first_name"])
            user_map[tm["first_name"]] = u
        self.stdout.write(self.style.SUCCESS(f"Ensured {len(user_map)} team members."))

        self.stdout.write(self.style.NOTICE("===> Seeding baseline contributions..."))
        # Sample items provided by user
        sample_activities = [
            # Arunbharathi in-progress large company contribution
            {
                "user": user_map.get("Arunbharathi"),
                "activity": "Built Attendance & Leave APIs and React UI, including leave and regularization workflows, employee management and access policies; source estimates about 20 working days.",
                "project_name": "Axinix Technologies",
                "scope": "Company Contribution",
                "category": "Development",
                "days": 20.0,
                "base": 11.0,
                "factors": (True, True, False, True, True, True), # 75%
                "status": "in_progress",
            },
            {
                "user": user_map.get("Arunbharathi"),
                "activity": "Added company/customer master, email-based invitations and client/organisation ticket tracking; source estimates about 20 working days.",
                "project_name": "Axinix Technologies",
                "scope": "Company Contribution",
                "category": "Development",
                "days": 20.0,
                "base": 9.5,
                "factors": (True, True, False, True, True, True), # 75%
                "status": "in_progress",
            },
            {
                "user": user_map.get("Arunbharathi"),
                "activity": "Integrated project management with ticket tracking to connect support work with developer verification and follow-up; about 10 days stated.",
                "project_name": "Axinix Technologies",
                "scope": "Company Contribution",
                "category": "Development",
                "days": 10.0,
                "base": 8.5,
                "factors": (True, True, False, True, True, True), # 75%
                "status": "in_progress",
            },
            {
                "user": user_map.get("Arunbharathi"),
                "activity": "Packaged the populate_core engine as a standalone reusable Django library with query DSL, RBAC policies, and audit logging.",
                "project_name": "Axinix Technologies",
                "scope": "Company Contribution",
                "category": "Reusable Component Development",
                "days": 1.0,
                "base": 11.0,
                "factors": (True, True, True, True, True, True), # 100%
                "status": "completed",
            },
            # Ajay sample items
            {
                "user": user_map.get("Ajay"),
                "activity": "Deployed working code to live and documented deployment commands for future use.",
                "project_name": "Sri KaliGuhan Clothing",
                "scope": "Project Contribution",
                "category": "Deployment & Server Maintenance",
                "days": 1.0,
                "base": 6.0,
                "factors": (True, True, True, True, True, True),
                "status": "completed",
            },
            {
                "user": user_map.get("Ajay"),
                "activity": "Configured S3 storage for images instead of local storage.",
                "project_name": "Sri KaliGuhan Clothing",
                "scope": "Project Contribution",
                "category": "Development",
                "days": 1.0,
                "base": 9.0,
                "factors": (True, True, True, True, True, True),
                "status": "completed",
            },
            # Siva Anna sample items
            {
                "user": user_map.get("Siva Anna"),
                "activity": "Met a manufacturing prospect, explained Workhub and gathered manufacturing requirements; opportunity remained on hold.",
                "project_name": "Manufacturing prospect",
                "scope": "Company Contribution",
                "category": "Business Development",
                "days": 1.0,
                "base": 9.0,
                "factors": (True, True, False, True, True, True),
                "status": "on_hold",
            },
            {
                "user": user_map.get("Siva Anna"),
                "activity": "Discussed textile inventory, e-commerce and marketplace integration with SKG Clothing MD and acquired an order.",
                "project_name": "Sri KaliGuhan Clothing",
                "scope": "Company Contribution",
                "category": "Client Acquisition",
                "days": 1.0,
                "base": 11.0,
                "factors": (True, True, True, True, True, True),
                "status": "completed",
            },
            # Rithika sample item
            {
                "user": user_map.get("Rithika"),
                "activity": "Created product knowledge document for guidance and operational training.",
                "project_name": "Axinix Technologies",
                "scope": "Company Contribution",
                "category": "Company Documentation",
                "days": 5.0,
                "base": 5.6,
                "factors": (True, True, False, True, True, True),
                "status": "in_progress",
            },
            # Karuppasamy sample item
            {
                "user": user_map.get("Karuppasamy"),
                "activity": "Reviewed system access permissions and initial environment setup.",
                "project_name": "Axinix Technologies",
                "scope": "Company Contribution",
                "category": "Company Operations & Administration",
                "days": 1.0,
                "base": 1.86,
                "factors": (True, True, False, True, True, True),
                "status": "in_progress",
            },
        ]

        created_count = 0
        for item in sample_activities:
            if not item["user"]:
                continue
            cat = ContributionCategory.objects.filter(name=item["category"]).first()
            f_eff, f_comp, f_del, f_qual, f_evid, f_out = item["factors"]

            # Calculate factor sum
            factor_sum = (
                (20.0 if f_eff else 0.0) +
                (15.0 if f_comp else 0.0) +
                (25.0 if f_del else 0.0) +
                (20.0 if f_qual else 0.0) +
                (10.0 if f_evid else 0.0) +
                (10.0 if f_out else 0.0)
            )
            final_points = round((item["days"] * item["base"]) * (factor_sum / 100.0), 2)

            WorkContribution.objects.get_or_create(
                user=item["user"],
                activity=item["activity"],
                defaults={
                    "date": timezone.now().date(),
                    "project_name": item["project_name"],
                    "scope": item["scope"],
                    "primary_category": cat,
                    "worked_days": item["days"],
                    "base_points": item["base"],
                    "factor_effort": f_eff,
                    "factor_complexity": f_comp,
                    "factor_deliverable": f_del,
                    "factor_quality": f_qual,
                    "factor_evidence": f_evid,
                    "factor_outcome": f_out,
                    "factor_percentage": factor_sum,
                    "final_points": final_points,
                    "delivery_status": item["status"],
                    "approval_status": "approved",
                    "lifecycle_status": 1,
                }
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} baseline work contribution entries."))
        self.stdout.write(self.style.SUCCESS("All contribution seed data successfully initialized!"))

