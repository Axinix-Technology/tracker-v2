import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-tracker-v2-axinix-core-dev-key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'populate_core',           # <--- Standalone Kernel package installed via pip
    'users',                   # <--- Core: Users, Roles, Org structure, Clients
    'tasks',                   # <--- Product: Tasks & Agile Project Tracker
    'tickets',                 # <--- Product: Helpdesk & Ticket System
    'attendance',              # <--- Product: Attendance & Shift Suite
    'notifications',           # <--- Core: Notifications & Receptionists
    'dashboard',               # <--- Core: Dashboard Layouts & Widgets
    'feed',                    # <--- Product: Social Feed & Team Collaboration
    'assets',                  # <--- Product: Asset Management & Equipment Lifecycle
    'hr',                      # <--- Product: Employee Documents, Policies & Progression
    'payroll',                 # <--- Product: Compensation, Payroll Runs, Payslips & Expenses
    'billing',                 # <--- Product: Client Invoicing, Quotations, OA, Payments & Double-Entry Ledgers
    'crm',                     # <--- Product: CRM Pipeline, Leads, Deals, Activities & Meetings
    'recruitment',             # <--- Product: Job Postings, Candidate Tracking & Employee Onboarding
    'system',                  # <--- Platform: Status Master, Email Config, Release Notes, Resources & Workflows
    'control_plane',           # <--- Control Plane: Multi-Tenant Provisioning, User Logins & Module Entitlements
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

USE_SQLITE = os.getenv('USE_SQLITE', 'False').strip().lower() in ('true', '1', 'yes')

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('DB_NAME', 'tracker_v2_dev.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('MYSQL_DATABASE', 'workhub_db'),
            'USER': os.getenv('MYSQL_USER', 'root'),
            'PASSWORD': os.getenv('MYSQL_PASSWORD', 'root@123'),
            'HOST': os.getenv('MYSQL_HOST', '127.0.0.1'),
            'PORT': os.getenv('MYSQL_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.DualTokenAndBearerAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

from corsheaders.defaults import default_headers

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:\d+$",
    r"^http://127\.0\.0\.1:\d+$",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-device-uuid',
    'x-tenant-id',
    'x-tenant-slug',
    'x-request-id',
    'deviceuuid',
]

# Populated Kernel Settings
POPULATE_CONFIG = {
    'ROLE_MODEL': 'users.Role',
    'SUPERADMIN_ROLE_FLAG': 'is_superadmin',
    'MAX_PREFETCH_DEPTH': 3,
    'CHILD_PAGINATION_CEILING': 50,
    'ENABLE_WORKFLOWS': True,
    'ENABLE_NOTIFICATIONS': True,
    'ENABLE_QUEUE': True,
    'PUBLIC_READ_MODELS': [
        'general_settings',
        'site_section_content',
        'site_section_contents',
        'company_profile',
        'company_profiles',
        'showcase_announcement',
        'showcase_announcements',
        'showcase_stat',
        'showcase_stats',
        'showcase_solution',
        'showcase_solutions',
        'showcase_industry',
        'showcase_industries',
        'showcase_service',
        'showcase_services',
        'showcase_portfolio',
        'showcase_portfolios',
        'showcase_testimonial',
        'showcase_testimonials',
        'showcase_category',
        'showcase_categories',
        'showcase_product',
        'showcase_products',
    ],
    'PUBLIC_CREATE_MODELS': [
        'website_inquiry',
        'website_inquiries',
    ],
}

SILENCED_SYSTEM_CHECKS = ['populate.E002']

