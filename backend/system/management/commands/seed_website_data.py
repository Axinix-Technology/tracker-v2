import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Role
from system.models import (
    SiteSectionContent,
    CompanyProfile,
    ShowcaseAnnouncement,
    ShowcaseStat,
    ShowcaseSolution,
    ShowcaseIndustry,
    ShowcaseService,
    ShowcasePortfolio,
    ShowcaseTestimonial,
    ShowcaseCategory,
    ShowcaseProduct,
)

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds database with comprehensive company website showcase data and creates the SuperAdmin user"

    def add_arguments(self, parser):
        parser.add_argument('--admin-username', type=str, default='admin', help='Admin username')
        parser.add_argument('--admin-email', type=str, default='admin@axinix.com', help='Admin email')
        parser.add_argument('--admin-password', type=str, default='Admin@123', help='Admin password')

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("==> Initializing Website Data Seed..."))

        admin_username = options['admin_username']
        admin_email = options['admin_email']
        admin_password = options['admin_password']

        # 1. SuperAdmin Role & User
        admin_role, _ = Role.objects.get_or_create(
            name="SuperAdmin",
            defaults={
                "description": "Full enterprise administrator with unrestricted platform access",
                "is_superadmin": True,
                "is_active": True,
                "status": 1,
            }
        )
        if not admin_role.is_superadmin:
            admin_role.is_superadmin = True
            admin_role.save()

        user = User.objects.filter(username=admin_username).first()
        if not user:
            user = User.objects.filter(email=admin_email).first()

        if not user:
            user = User.objects.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                first_name="Website",
                last_name="Admin",
            )
            self.stdout.write(self.style.SUCCESS(f"Created Admin User: {admin_username} ({admin_email})"))
        else:
            user.set_password(admin_password)
            self.stdout.write(self.style.WARNING(f"Updated password for Admin User: {user.username}"))

        user.role = admin_role
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # 2. Company Profile
        CompanyProfile.objects.update_or_create(
            name="AXINIX Technologies",
            defaults={
                "legal_name": "Axinix Technologies Pvt. Ltd.",
                "tagline": "Powering Every Industry. Enabling Every Possibility.",
                "about_text": "Axinix Technologies Pvt. Ltd. is a modern technology enterprise with the vision 'Leverage Technology to Enable Outcomes that Matter', focusing on intelligent ERP, retail POS, cloud architecture, and business automation.",
                "logo_url": "/axinix-brand-mark.jpg",
                "website": "https://www.axinixtech.com",
                "contact_email": "prism@axinixtech.com",
                "hr_email": "hr@axinixtech.com",
                "it_email": "it@axinixtech.com",
                "phone": "+91 98765 43210",
                "address": {
                    "street": "Technology Innovation Center, Main Road",
                    "city": "Coimbatore",
                    "state": "Tamil Nadu",
                    "country": "India",
                    "zip": "641001"
                },
                "social_links": {
                    "linkedin": "https://linkedin.com/company/axinix",
                    "twitter": "https://twitter.com/axinixtech",
                    "github": "https://github.com/axinix",
                    "youtube": "https://youtube.com/@axinix"
                },
                "is_active": True,
            }
        )
        self.stdout.write("✓ Company Profile seeded")

        # 3. Site Section Content (Hero, Marquee, CTA, Comparison, Why Choose Us, Process Roadmap)
        sections = [
            {
                "section_key": "home_hero",
                "title": "Powering Every Industry.",
                "subtitle": "From intelligent enterprise ERP and high-velocity retail POS to cloud architecture and digital applications, AXINIX streamlines multi-branch operations and accelerates business growth.",
                "badge": "AXINIX TECHNOLOGIES",
                "content": {
                    "highlight": "Enabling Every Possibility.",
                    "primaryAction": {"label": "Explore Our Solutions", "to": "/solutions"},
                    "secondaryAction": {"label": "Book a Consultation", "to": "/contact"}
                }
            },
            {
                "section_key": "home_cta",
                "title": "Let's Build Something Powerful Together.",
                "subtitle": "Tell us about your business goals and operational challenges. Our technology architects will demonstrate the exact software solution built for you.",
                "badge": "START YOUR TRANSFORMATION",
                "content": {
                    "primaryAction": {"label": "Contact Our Specialists", "to": "/contact"},
                    "secondaryAction": {"label": "Explore Solutions", "to": "/solutions"}
                }
            },
            {
                "section_key": "home_why_choose_us",
                "title": "Why Forward-Thinking Businesses Choose AXINIX",
                "subtitle": "We engineer business software that empowers your team, eliminates manual errors, and unlocks tangible ROI from day one.",
                "badge": "THE AXINIX ADVANTAGE",
                "content": {
                    "items": [
                        {"title": "Multi-Industry Expertise", "description": "Deep domain knowledge across textiles, retail, manufacturing, education, and hospitality."},
                        {"title": "Complete Digital Solutions", "description": "From core backend ERPs and POS to public websites, mobile apps, and digital marketing."},
                        {"title": "Customisable Software", "description": "Modular systems designed to adapt to your unique workflows, rather than forcing rigid templates."},
                        {"title": "Business Automation", "description": "Eliminate tedious manual re-entry and let intelligent automated rules run your operations."},
                        {"title": "Scalable Technology", "description": "Built on modern cloud architecture engineered to grow from 1 store to 100+ branches effortlessly."},
                        {"title": "Dedicated Support", "description": "Direct human assistance, rapid response times, and ongoing system optimization."},
                        {"title": "Customer-Focused Approach", "description": "We measure our success by the tangible business growth and time saved by our clients."},
                        {"title": "Continuous Improvement", "description": "Regular feature enhancements, regulatory tax compliance updates, and security hardening."}
                    ]
                }
            },
            {
                "section_key": "home_process_roadmap",
                "title": "Our Proven Implementation Methodology",
                "subtitle": "From initial discovery to post-launch optimization, our five-stage engineering roadmap ensures zero downtime and rapid user adoption.",
                "badge": "HOW WE DELIVER SUCCESS",
                "content": {
                    "steps": [
                        {"number": "01", "title": "Understand", "description": "We listen deeply to your business operations, goals, pain points, and existing workflows.", "icon": "Compass"},
                        {"number": "02", "title": "Analyse", "description": "Our system architects study operational bottlenecks, data flows, and technical requirements.", "icon": "SearchCheck"},
                        {"number": "03", "title": "Plan", "description": "We recommend the exact technology stack, software architecture, milestones, and deployment roadmap.", "icon": "CalendarClock"},
                        {"number": "04", "title": "Develop", "description": "We engineer robust, responsive, and secure software following rigorous coding and security standards.", "icon": "Code2"},
                        {"number": "05", "title": "Deliver", "description": "We deploy, train your personnel, verify audit trails, and deliver continuous support.", "icon": "ShieldCheck"}
                    ]
                }
            },
            {
                "section_key": "footer_meta",
                "title": "AXINIX Technologies",
                "subtitle": "Make New Generation Applications. Conglomerate with the vision to leverage technology to enable outcomes that matter.",
                "badge": "2026",
                "content": {
                    "copyright": "© 2026 AXINIX Technologies Pvt. Ltd. All rights reserved.",
                    "supportHotline": "+91 98765 43210",
                    "officeHours": "Mon - Sat: 9:00 AM - 6:30 PM IST"
                }
            }
        ]
        for sec in sections:
            SiteSectionContent.objects.update_or_create(
                section_key=sec["section_key"],
                defaults=sec
            )
        self.stdout.write("✓ Site Section Content seeded")

        # 4. Announcements
        announcements = [
            ("Complete Business Technology Solutions.", 1),
            ("Smart Software for Every Industry.", 2),
            ("Transform Your Business with AXINIX.", 3),
        ]
        ShowcaseAnnouncement.objects.all().delete()
        for idx, (text, order) in enumerate(announcements, 1):
            ShowcaseAnnouncement.objects.create(
                title=text,
                order=order,
                is_active=True
            )
        self.stdout.write("✓ Announcements seeded")

        # 5. Stats
        stats = [
            {"label": "Businesses Served", "value": "150+", "change": "+24% YoY", "order": 1},
            {"label": "Projects Delivered", "value": "320+", "change": "100% on-time", "order": 2},
            {"label": "Industries Supported", "value": "16+", "change": "Comprehensive", "order": 3},
            {"label": "Years of Experience", "value": "8+", "change": "Enterprise focus", "order": 4},
            {"label": "Customer Satisfaction", "value": "99.4%", "change": "Verified rating", "order": 5},
        ]
        ShowcaseStat.objects.all().delete()
        for item in stats:
            ShowcaseStat.objects.create(**item, is_active=True)
        self.stdout.write("✓ Stats seeded")

        # 6. Solutions
        solutions = [
            {
                "slug": "erp",
                "title": "ERP Software",
                "subtitle": "Run your whole business from one unified system.",
                "description": "Intelligent Enterprise Resource Planning software connecting supply chain, sales, warehouse, branch accounting, and multi-location operations into a single real-time dashboard.",
                "badge": "Enterprise Core",
                "icon": "Layers",
                "features": [
                    "Business Management & Governance",
                    "Sales & Purchase Order Automation",
                    "Multi-Warehouse Inventory Control",
                    "Financial Accounting & Tax Invoicing",
                    "Branch & Franchise Management",
                    "Real-time Reporting & Executive Analytics",
                    "Employee & Department Role Access"
                ],
                "benefits": [
                    "Eliminate manual data re-entry across disconnected systems",
                    "Full visibility into enterprise cash flows and stock levels",
                    "Automated approval workflows and audit trails",
                    "Role-based permission security (RBAC) across branches"
                ],
                "mock_metrics": {"kpi1": "99.8% Sync", "kpi2": "14 Branches", "kpi3": "Live Ledger"},
                "order": 1,
            },
            {
                "slug": "crm",
                "title": "CRM Software",
                "subtitle": "Turn leads into loyal customers with intelligent pipeline tracking.",
                "description": "Full-cycle customer relationship platform with automated lead capture, omnichannel communication logs, sales opportunity stages, and predictive follow-up reminders.",
                "badge": "Growth Engine",
                "icon": "Users",
                "features": [
                    "Lead Capture & Automatic Assignment",
                    "Comprehensive Customer 360 Database",
                    "Visual Sales Opportunity Pipeline",
                    "Follow-up Task & Reminder System",
                    "Omnichannel Customer Communication (WhatsApp/Email)",
                    "Conversion & Team Sales Analytics"
                ],
                "benefits": [
                    "Never lose a prospective lead with automated alerts",
                    "Track deal velocity and stage drop-offs accurately",
                    "Centralize customer communication history in one timeline",
                    "Empower sales managers with real-time conversion metrics"
                ],
                "mock_metrics": {"kpi1": "3.4x Leads", "kpi2": "88% Retention", "kpi3": "Zero Drop-offs"},
                "order": 2,
            },
            {
                "slug": "pos",
                "title": "POS & Retail Management",
                "subtitle": "Fast billing, lightning barcode lookup, and live stock across stores.",
                "description": "High-speed retail point-of-sale system engineered for high-throughput checkout counters, thermal receipt printing, returns management, and real-time inventory deduction.",
                "badge": "High Throughput",
                "icon": "Store",
                "features": [
                    "Sub-Second Barcode Billing & Thermal Printing",
                    "Multi-Store Inventory Synchronization",
                    "Integrated Loyalty Points & Discounts",
                    "Supplier Purchase Orders & Goods Receipt",
                    "Centralized Price Book & Promotion Rules",
                    "Returns, Exchanges & Credit Notes Handling",
                    "Daily Drawer Reconciliation & Cash Audits"
                ],
                "benefits": [
                    "Cut counter queues in half during peak hours",
                    "Avoid stockout surprises through instant cross-store stock check",
                    "Flexible tax and barcode format support",
                    "Offline-capable billing with background sync"
                ],
                "mock_metrics": {"kpi1": "<1.2s Scan", "kpi2": "100% Offline OK", "kpi3": "12 Stores Live"},
                "order": 3,
            },
            {
                "slug": "hrms",
                "title": "HRMS & Payroll",
                "subtitle": "People operations, biometric attendance, and automated payroll without paperwork.",
                "description": "Modern human resource management suite delivering biometric attendance sync, automated salary calculation, leave approvals, employee self-service portals, and compliance reporting.",
                "badge": "HR Suite",
                "icon": "Briefcase",
                "features": [
                    "Employee Digital Profiles & Document Vault",
                    "Biometric & Geofenced Mobile Attendance",
                    "Tiered Leave Management & Approvals",
                    "One-Click Automated Payroll & Payslips",
                    "Statutory Deductions & Compliance (PF, ESI, Tax)",
                    "Performance Reviews & KPI Appraisals"
                ],
                "benefits": [
                    "Generate payroll in minutes with zero mathematical errors",
                    "Eliminate attendance disputes with biometric timestamps",
                    "Self-service mobile dashboard for leave requests and payslips",
                    "Encrypted employee document storage with audit history"
                ],
                "mock_metrics": {"kpi1": "100% Compliant", "kpi2": "0 Payroll Errors", "kpi3": "Self-Serve App"},
                "order": 4,
            },
            {
                "slug": "inv",
                "title": "Inventory Management",
                "subtitle": "Know exactly what you have, in every warehouse, in real time.",
                "description": "Granular stock control system supporting batch tracking, serial numbers, expiration date warnings, reorder thresholds, and bin-level warehouse movements.",
                "badge": "Supply Chain",
                "icon": "Package",
                "features": [
                    "Multi-Warehouse & Bin Location Tracking",
                    "Batch Number & Expiry Date Management",
                    "Automated Low Stock & Reorder Triggers",
                    "Inter-Branch Stock Transfer Workflows",
                    "Cycle Counting & Physical Stock Audits",
                    "Supplier Lead Time & Procurement Planning"
                ],
                "benefits": [
                    "Prevent dead inventory and costly stock write-offs",
                    "Automated purchase indenting based on consumption trends",
                    "Complete traceability from vendor shipment to customer delivery",
                    "Eliminate shrinkage with mandatory dispatch verifications"
                ],
                "mock_metrics": {"kpi1": "99.9% Accuracy", "kpi2": "Zero Dead Stock", "kpi3": "Auto-Reorder"},
                "order": 5,
            },
            {
                "slug": "acc",
                "title": "Accounting & Finance",
                "subtitle": "Crystal-clear books, multi-currency ledgers, and live cash flow visibility.",
                "description": "Double-entry accounting engine fully compliant with standard financial regulations. Features automated bank reconciliation, expense vouchers, GST/VAT filings, and P&L dashboards.",
                "badge": "Financial Governance",
                "icon": "DollarSign",
                "features": [
                    "Double-Entry Chart of Accounts & General Ledger",
                    "Accounts Payable & Receivable Automation",
                    "Bank Statement Feed & One-Click Reconciliation",
                    "Automated Tax Calculation (GST / VAT / TDS)",
                    "Profit & Loss, Balance Sheet & Cashflow Statements"
                ],
                "benefits": [
                    "Auditor-ready financial statements in one click",
                    "Track receivables with automated payment reminder emails",
                    "Real-time expense variance vs budgeted amounts",
                    "Multi-branch consolidated balance sheets"
                ],
                "mock_metrics": {"kpi1": "Audit-Ready", "kpi2": "Live Cashflow", "kpi3": "Instant P&L"},
                "order": 6,
            }
        ]
        for item in solutions:
            ShowcaseSolution.objects.update_or_create(
                slug=item["slug"],
                defaults={**item, "is_active": True}
            )
        self.stdout.write("✓ Solutions seeded")

        # 7. Industries
        industries = [
            {
                "slug": "textile",
                "name": "Textile & Fashion",
                "category": "Retail & Manufacturing",
                "subtitle": "Streamline fabric sourcing, job-work processing, barcoded garment retail, and seasonal catalogs.",
                "challenges": [
                    "Managing diverse rolls, fabrics, shades, sizes, and colour variants (SKUs)",
                    "Discrepancies in job-worker and dying mill cut-piece reconciliation",
                    "Balancing retail showroom stock with wholesale dispatch orders",
                    "Rapid seasonal inventory obsolescence and markdown pressure"
                ],
                "features": [
                    "Textile ERP with Fabric Matrix & GSM/Meter Calculation",
                    "Job-Work Challan Tracking (Dyeing, Weaving, Embroidery)",
                    "Retail POS with Size & Colour Barcode Tags",
                    "Wholesale Pack Ordering & Broker Commission Tracking",
                    "Integrated Fashion E-Commerce Catalog & Instagram Sync"
                ],
                "popular_services": ["web", "ecom", "retailsrv", "marketing"],
                "order": 1,
            },
            {
                "slug": "retail",
                "name": "Supermarkets & Retail Chains",
                "category": "Retail & FMCG",
                "subtitle": "High-throughput barcode billing, centralized purchasing, supplier credit notes, and store replenishment.",
                "challenges": [
                    "Severe billing counter queues during evening rush hours",
                    "Managing tens of thousands of FMCG SKUs and fast-expiring batches",
                    "Coordinating inter-store transfers without inventory mismatches",
                    "Tracking supplier credit notes, rebates, and purchase returns"
                ],
                "features": [
                    "Lightning Barcode Billing POS (<1.2s per scan)",
                    "Batch-Wise Expiry Management & Automated Clearance Markdowns",
                    "Centralized Multi-Store Purchasing & Reorder Suggestions",
                    "Integrated Customer Loyalty Points & WhatsApp Digital Invoices",
                    "Offline-Resilient Counter Sync Architecture"
                ],
                "popular_services": ["retailsrv", "poshardware", "inventory", "mobile"],
                "order": 2,
            },
            {
                "slug": "manufacturing",
                "name": "Manufacturing & Fabrication",
                "category": "Industrial Production",
                "subtitle": "Complete Bill of Materials (BOM), shop-floor job cards, scrap tracking, and machine maintenance.",
                "challenges": [
                    "Inaccurate raw material consumption reporting leading to stockouts",
                    "Tracking semi-finished goods (WIP) across multiple assembly work centers",
                    "Machine downtime causing production schedule slippages",
                    "Calculating accurate per-unit landed costs including overheads"
                ],
                "features": [
                    "Multi-Level Bill of Materials (BOM) & Scrap Rate Tracking",
                    "Shop-Floor Job Card Tracking via Rugged Tablets / Barcodes",
                    "Preventive Machine Maintenance Schedules & Breakdown Logs",
                    "Automated Per-Batch Finished Goods Costing Engine",
                    "Supplier Quality Inspection & Goods Receipt Notes (GRN)"
                ],
                "popular_services": ["custom", "erp", "cloud", "qa"],
                "order": 3,
            },
            {
                "slug": "healthcare",
                "name": "Healthcare & Clinics",
                "category": "Medical & Clinical",
                "subtitle": "Digital patient records, outpatient appointments, doctor consultation queues, and pharmacy billing.",
                "challenges": [
                    "Lost patient medical history across paper files and disconnected clinics",
                    "Unpredictable outpatient waiting times and chaotic consultation queues",
                    "Managing pharmacy inventory with strict drug expiry compliance",
                    "Protecting patient health records (HIPAA & local medical data privacy)"
                ],
                "features": [
                    "Electronic Medical Records (EMR) & Digital Prescription Vault",
                    "Online Appointment Scheduling & Live Queue Display Boards",
                    "Integrated Pharmacy POS with Batch & Drug Expiry Alerts",
                    "Diagnostic Lab Test Order Tracking & Automated WhatsApp Reports",
                    "Role-Based Patient Record Privacy Controls"
                ],
                "popular_services": ["custom", "mobile", "security", "cloud"],
                "order": 4,
            }
        ]
        for item in industries:
            ShowcaseIndustry.objects.update_or_create(
                slug=item["slug"],
                defaults={**item, "is_active": True}
            )
        self.stdout.write("✓ Industries seeded")

        # 8. Services
        services = [
            {
                "slug": "web",
                "title": "Website Development",
                "subtitle": "High-performance corporate portals, responsive landing pages, and custom web applications.",
                "description": "We engineer bespoke, lightning-fast digital storefronts and corporate websites engineered for maximum search visibility, mobile responsiveness, and enterprise brand authority.",
                "features": [
                    "Modern High-Converting Business Websites",
                    "Corporate Portals with CMS Integration",
                    "Interactive Portfolio & Showcase Websites",
                    "Fast-Loading Lead Generation Landing Pages",
                    "Strict W3C & WCAG Accessibility Compliance",
                    "Ongoing Security Hardening & Maintenance"
                ],
                "deliverables": [
                    "Production-ready responsive website with source code",
                    "Search Engine Optimization (SEO) setup & Schema markup",
                    "Fast CDN deployment (Vercel / AWS CloudFront)",
                    "Interactive contact inquiry pipeline integration"
                ],
                "order": 1,
            },
            {
                "slug": "mobile",
                "title": "Mobile App Development",
                "subtitle": "Native and cross-platform mobile apps for iOS and Android that customers and teams love.",
                "description": "From customer-facing loyalty apps to field staff tracking tools, we build smooth, high-fidelity Flutter and React Native mobile applications backed by reliable cloud APIs.",
                "features": [
                    "Cross-Platform Flutter & React Native Engineering",
                    "Offline-First Architecture with Local Data Sync",
                    "Push Notifications via Firebase Cloud Messaging (FCM)",
                    "Biometric Login (FaceID / Fingerprint Authentication)",
                    "App Store & Google Play Store Submission Assistance"
                ],
                "deliverables": [
                    "Production Android APK/AAB and iOS IPA build packages",
                    "Fully tested REST API integration layer",
                    "Push notification setup & automated deep-linking",
                    "Source repository with CI/CD build scripts"
                ],
                "order": 2,
            },
            {
                "slug": "custom",
                "title": "Custom Software Development",
                "subtitle": "Tailored enterprise solutions built precisely around your operational blueprint.",
                "description": "When off-the-shelf software falls short, we design and build bespoke software systems engineered specifically to solve your proprietary operational challenges.",
                "features": [
                    "Custom Enterprise Applications & Internal Portals",
                    "Third-Party API Integrations (Payment Gateways, ERPs, CRMs)",
                    "Legacy System Modernization & Cloud Migration",
                    "Automated Data Extraction & ETL Pipelines",
                    "Microservices & Event-Driven Architecture"
                ],
                "deliverables": [
                    "Enterprise software solution with full intellectual property transfer",
                    "API contracts, Swagger documentation & database schema maps",
                    "Automated integration test suites",
                    "Dedicated SLA support agreement"
                ],
                "order": 3,
            },
            {
                "slug": "cloud",
                "title": "Cloud, DevOps & IT Infrastructure",
                "subtitle": "High-availability cloud infrastructure, zero-downtime CI/CD, and server management.",
                "description": "We architect scalable, cost-optimized, and resilient cloud environments on AWS, Azure, and Google Cloud, ensuring your business software operates without interruption.",
                "features": [
                    "Cloud Architecture Design & Infrastructure as Code (Terraform)",
                    "Automated CI/CD Pipelines (GitHub Actions / GitLab)",
                    "Containerization & Orchestration (Docker & Kubernetes)",
                    "24/7 Monitoring, Alerting & Uptime Observability",
                    "Automated Disaster Recovery & Database Backup Verification"
                ],
                "deliverables": [
                    "Production cloud infrastructure with high availability",
                    "Automated CI/CD build & deployment pipelines",
                    "Real-time observability dashboard (Grafana / CloudWatch)",
                    "Disaster recovery & snapshot backup runbooks"
                ],
                "order": 4,
            }
        ]
        for item in services:
            ShowcaseService.objects.update_or_create(
                slug=item["slug"],
                defaults={**item, "is_active": True}
            )
        self.stdout.write("✓ Services seeded")

        # 9. Portfolio
        portfolios = [
            {
                "slug": "textile-erp-rollout",
                "title": "Enterprise Textile ERP Rollout",
                "category": "ERP Implementations",
                "industry": "Textile & Fashion",
                "industry_slug": "textile",
                "tags": ["ERP", "POS", "Multi-Branch"],
                "client": "Premier Textile Mills",
                "challenge": "Scattered inventory across 6 dyeing units, 3 warehouses, and 12 retail showrooms led to recurring stockouts and inaccurate yarn consumption records.",
                "solution": "Deployed AXINIX Enterprise Textile ERP with fabric roll barcode tagging, automated job-work challan reconciliations, and real-time branch sales consolidation.",
                "results": [
                    "38% reduction in cut-piece scrap material wastage",
                    "Eliminated stock reconciliation delays from 4 days to real time",
                    "Connected all 12 retail branches to centralized billing"
                ],
                "order": 1,
            },
            {
                "slug": "supermarket-pos-modernization",
                "title": "Multi-Store Supermarket POS Modernization",
                "category": "Retail POS Systems",
                "industry": "Supermarkets & Retail Chains",
                "industry_slug": "retail",
                "tags": ["POS", "Inventory", "Retail"],
                "client": "Grand Fresh Mart Chain",
                "challenge": "Heavy evening counter queues with scan delays exceeding 4 seconds per item, alongside weekly stock variances across 8 supermarket locations.",
                "solution": "Implemented AXINIX High-Velocity POS with sub-second barcode indexing, automated purchase indenting, and WhatsApp digital invoicing.",
                "results": [
                    "Checkout time reduced by 58% during peak hours",
                    "Automated expiry markdowns saved ₹4.2 Lakhs annually in spoiled goods",
                    "Paper receipt cost reduced by 70% via WhatsApp e-invoices"
                ],
                "order": 2,
            }
        ]
        for item in portfolios:
            ShowcasePortfolio.objects.update_or_create(
                slug=item["slug"],
                defaults={**item, "is_active": True}
            )
        self.stdout.write("✓ Portfolio seeded")

        # 10. Testimonials
        testimonials = [
            {
                "client": "Rajesh Textiles",
                "role": "Textile Retailer & Wholesaler",
                "quote": "The AXINIX team understood our multi-branch fabric stock process immediately. The unified ERP system eliminated our inventory mismatches and cut counter checkout time in half.",
                "rating": 5,
                "location": "Surat, Gujarat",
                "order": 1,
            },
            {
                "client": "Prime Mart Supermarkets",
                "role": "Supermarket Operations Director",
                "quote": "Switching to AXINIX Retail POS transformed our checkout flow during festive rushes. The offline reliability ensures billing never stops even if store internet fluctuates.",
                "rating": 5,
                "location": "Coimbatore, Tamil Nadu",
                "order": 2,
            },
            {
                "client": "Precision Engineering Works",
                "role": "Managing Director",
                "quote": "AXINIX engineered a bespoke job-card and machine allocation system that gave us complete visibility into factory floor costs. We now quote projects with 100% confidence.",
                "rating": 5,
                "location": "Bengaluru, Karnataka",
                "order": 3,
            }
        ]
        ShowcaseTestimonial.objects.all().delete()
        for item in testimonials:
            ShowcaseTestimonial.objects.create(**item, is_active=True)
        self.stdout.write("✓ Testimonials seeded")

        # 11. Categories & Products
        categories = [
            {
                "slug": "software-suites",
                "name": "Enterprise Software Suites",
                "badge": "Core Platform",
                "icon": "Layers",
                "item_count": 4,
                "description": "Mission-critical enterprise software suites including ERP, CRM, POS, and HRMS for scalable multi-branch governance.",
                "order": 1,
            },
            {
                "slug": "retail-hardware",
                "name": "Retail & POS Hardware",
                "badge": "Hardware Kits",
                "icon": "Store",
                "item_count": 3,
                "description": "Certified high-reliability retail hardware bundles: thermal printers, omnidirectional barcode scanners, and touch POS terminals.",
                "order": 2,
            }
        ]
        for item in categories:
            ShowcaseCategory.objects.update_or_create(
                slug=item["slug"],
                defaults={**item, "is_active": True}
            )

        products = [
            {
                "slug": "erp-cloud-pro",
                "sku": "AX-ERP-CLD-PRO",
                "name": "AXINIX ERP Cloud - Professional Edition",
                "category_slug": "software-suites",
                "category_name": "Enterprise Software Suites",
                "tagline": "Annual subscription for up to 10 users with multi-branch sync and financial reporting.",
                "price": 48000.00,
                "original_price": 60000.00,
                "features": ["10 User Accounts", "Multi-Warehouse Inventory", "GST Tax Invoicing", "24/7 Support"],
                "order": 1,
            },
            {
                "slug": "pos-retail-pack",
                "sku": "AX-POS-STORE-PK",
                "name": "AXINIX Retail POS Store Package",
                "category_slug": "software-suites",
                "category_name": "Enterprise Software Suites",
                "tagline": "High-speed retail counter package with offline support and barcode generator.",
                "price": 24000.00,
                "original_price": 30000.00,
                "features": ["Sub-Second Barcode Billing", "Thermal Printing Support", "Daily Cash Audit", "WhatsApp Invoices"],
                "order": 2,
            }
        ]
        for item in products:
            ShowcaseProduct.objects.update_or_create(
                slug=item["slug"],
                defaults={**item, "is_active": True}
            )
        self.stdout.write("✓ Categories and Products seeded")

        self.stdout.write(self.style.SUCCESS("\n==> SUCCESS: All website showcase data and SuperAdmin seeded successfully!"))
        self.stdout.write(self.style.SUCCESS(f"    Admin Login: {admin_username} / Password: {admin_password}"))

