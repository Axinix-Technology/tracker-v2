from django.db import models
from populate_core.registry import register_model


# ============================================================================
# 1. SITE SECTION CONTENT (FLEXIBLE 100% FIELD REGISTRY FOR ANY HERO/BANNER/CTA)
# ============================================================================

@register_model(
    "site_section_content",
    table_type="master",
    aliases=["site_section_contents", "section_content", "section_contents"],
    search_fields=["section_key", "title", "subtitle"],
    status_field="is_active",
    public_fields=["section_key", "title", "subtitle", "badge", "content", "is_active", "status"]
)
class SiteSectionContent(models.Model):
    section_key = models.CharField(max_length=128, unique=True, db_index=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)
    badge = models.CharField(max_length=128, blank=True, null=True)
    content = models.JSONField(default=dict, blank=True, help_text="Flexible content for buttons, cards, links")
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_site_section_contents"
        ordering = ["section_key"]

    def __str__(self):
        return f"Section: {self.section_key} ({self.title})"


# ============================================================================
# 2. COMPANY PROFILE (BRANDING, CONTACT, HEADQUARTERS)
# ============================================================================

@register_model(
    "company_profile",
    table_type="master",
    aliases=["company_profiles", "companyprofile"],
    search_fields=["name", "legal_name", "tagline", "contact_email"],
    status_field="is_active",
    public_fields=[
        "name", "legal_name", "tagline", "about_text", "logo_url", "website",
        "contact_email", "hr_email", "it_email", "phone", "address", "social_links", "is_active", "status"
    ]
)
class CompanyProfile(models.Model):
    name = models.CharField(max_length=255, default="AXINIX Technologies")
    legal_name = models.CharField(max_length=255, default="Axinix Technologies Pvt. Ltd.")
    tagline = models.CharField(max_length=255, blank=True, null=True)
    about_text = models.TextField(blank=True, null=True)
    logo_url = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    hr_email = models.EmailField(blank=True, null=True)
    it_email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    address = models.JSONField(default=dict, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_company_profiles"

    def __str__(self):
        return self.name


# ============================================================================
# 3. SHOWCASE ANNOUNCEMENTS (ANIMATED TICKER)
# ============================================================================

@register_model(
    "showcase_announcement",
    table_type="master",
    aliases=["showcase_announcements", "announcements"],
    search_fields=["title"],
    status_field="is_active",
    public_fields=["title", "link_url", "order", "is_active", "status"]
)
class ShowcaseAnnouncement(models.Model):
    title = models.CharField(max_length=255)
    link_url = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_showcase_announcements"
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title


# ============================================================================
# 4. SHOWCASE STATS (KPI & METRICS)
# ============================================================================

@register_model(
    "showcase_stat",
    table_type="master",
    aliases=["showcase_stats", "stats"],
    search_fields=["label", "value"],
    status_field="is_active",
    public_fields=["label", "value", "change", "order", "is_active", "status"]
)
class ShowcaseStat(models.Model):
    label = models.CharField(max_length=128)
    value = models.CharField(max_length=64)
    change = models.CharField(max_length=64, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_showcase_stats"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.label}: {self.value}"


# ============================================================================
# 5. SHOWCASE SOLUTIONS (ERP, CRM, POS, HRMS, INVENTORY, ACCOUNTING)
# ============================================================================

@register_model(
    "showcase_solution",
    table_type="master",
    aliases=["showcase_solutions", "solutions"],
    search_fields=["slug", "title", "subtitle", "description"],
    status_field="is_active",
    public_fields=["slug", "title", "subtitle", "description", "badge", "icon", "features", "benefits", "mock_metrics", "order", "is_active", "status"]
)
class ShowcaseSolution(models.Model):
    slug = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=128)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    badge = models.CharField(max_length=64, blank=True, null=True)
    icon = models.CharField(max_length=64, default="Layers")
    features = models.JSONField(default=list, blank=True)
    benefits = models.JSONField(default=list, blank=True)
    mock_metrics = models.JSONField(default=dict, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_showcase_solutions"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.title} ({self.slug})"


# ============================================================================
# 6. SHOWCASE INDUSTRIES (TEXTILE, HEALTHCARE, RETAIL, MANUFACTURING)
# ============================================================================

@register_model(
    "showcase_industry",
    table_type="master",
    aliases=["showcase_industries", "industries"],
    search_fields=["slug", "name", "category", "subtitle"],
    status_field="is_active",
    public_fields=["slug", "name", "category", "subtitle", "challenges", "features", "popular_services", "order", "is_active", "status"]
)
class ShowcaseIndustry(models.Model):
    slug = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=128, default="General")
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    challenges = models.JSONField(default=list, blank=True)
    features = models.JSONField(default=list, blank=True)
    popular_services = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_showcase_industries"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} ({self.slug})"


# ============================================================================
# 7. SHOWCASE SERVICES (WEB, MOBILE, CLOUD, DEVOPS)
# ============================================================================

@register_model(
    "showcase_service",
    table_type="master",
    aliases=["showcase_services", "services"],
    search_fields=["slug", "title", "subtitle", "description"],
    status_field="is_active",
    public_fields=["slug", "title", "subtitle", "description", "features", "deliverables", "order", "is_active", "status"]
)
class ShowcaseService(models.Model):
    slug = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=128)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    features = models.JSONField(default=list, blank=True)
    deliverables = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_showcase_services"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.title} ({self.slug})"


# ============================================================================
# 8. SHOWCASE PORTFOLIO (CASE STUDIES & SUCCESS STORIES)
# ============================================================================

@register_model(
    "showcase_portfolio",
    table_type="master",
    aliases=["showcase_portfolios", "portfolios", "portfolio"],
    search_fields=["slug", "title", "client", "category", "industry"],
    status_field="is_active",
    public_fields=["slug", "title", "category", "industry", "industry_slug", "tags", "client", "challenge", "solution", "results", "order", "is_active", "status"]
)
class ShowcasePortfolio(models.Model):
    slug = models.CharField(max_length=128, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=128, default="Case Studies")
    industry = models.CharField(max_length=128, blank=True, null=True)
    industry_slug = models.CharField(max_length=64, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    client = models.CharField(max_length=255, blank=True, null=True)
    challenge = models.TextField(blank=True, null=True)
    solution = models.TextField(blank=True, null=True)
    results = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_showcase_portfolios"
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title


# ============================================================================
# 9. SHOWCASE TESTIMONIALS (CLIENT REVIEWS & RATINGS)
# ============================================================================

@register_model(
    "showcase_testimonial",
    table_type="master",
    aliases=["showcase_testimonials", "testimonials"],
    search_fields=["client", "role", "quote", "location"],
    status_field="is_active",
    public_fields=["client", "role", "quote", "rating", "location", "avatar_url", "order", "is_active", "status"]
)
class ShowcaseTestimonial(models.Model):
    client = models.CharField(max_length=255)
    role = models.CharField(max_length=128, blank=True, null=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    location = models.CharField(max_length=128, blank=True, null=True)
    avatar_url = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_showcase_testimonials"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.client} ({self.rating} stars)"


# ============================================================================
# 10. SHOWCASE CATEGORIES & PRODUCTS (COMMERCIAL SUITES & PRICING)
# ============================================================================

@register_model(
    "showcase_category",
    table_type="master",
    aliases=["showcase_categories", "categories"],
    search_fields=["slug", "name", "badge", "description"],
    status_field="is_active",
    public_fields=["slug", "name", "badge", "icon", "item_count", "description", "order", "is_active", "status"]
)
class ShowcaseCategory(models.Model):
    slug = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=128)
    badge = models.CharField(max_length=64, blank=True, null=True)
    icon = models.CharField(max_length=64, default="Layers")
    item_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_showcase_categories"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} ({self.slug})"


@register_model(
    "showcase_product",
    table_type="master",
    aliases=["showcase_products"],
    search_fields=["slug", "sku", "name", "tagline"],
    status_field="is_active",
    public_fields=["slug", "sku", "name", "category_slug", "category_name", "tagline", "price", "original_price", "features", "order", "is_active", "status"]
)
class ShowcaseProduct(models.Model):
    slug = models.CharField(max_length=64, unique=True, db_index=True)
    sku = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=255)
    category_slug = models.CharField(max_length=64, db_index=True)
    category_name = models.CharField(max_length=128, blank=True, null=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    features = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    status = models.SmallIntegerField(default=1, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_showcase_products"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} ({self.sku})"


# ============================================================================
# 11. WEBSITE INQUIRIES (REAL-TIME LEADS FROM CONTACT FORM)
# ============================================================================

@register_model(
    "website_inquiry",
    table_type="transaction",
    aliases=["website_inquiries", "inquiries"],
    search_fields=["full_name", "email", "phone", "company", "service_needed", "status"],
    status_field="status",
    public_fields=["full_name", "email", "phone", "company", "industry", "service_needed", "message", "status", "created_at"]
)
class WebsiteInquiry(models.Model):
    full_name = models.CharField(max_length=128)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=128, blank=True, null=True)
    service_needed = models.CharField(max_length=128, blank=True, null=True)
    message = models.TextField()
    status = models.CharField(max_length=32, default="New", db_index=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_website_inquiries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Inquiry from {self.full_name} ({self.email}) - {self.status}"

