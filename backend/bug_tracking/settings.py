"""
Django settings for bug_tracking project.
"""

import sys
from datetime import timedelta
from pathlib import Path

from decouple import config

from .security import (
    parse_allowed_hosts,
    parse_origins,
    production_security_settings,
    resolve_secret_key,
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# pytest imports this module after pytest itself is loaded. Default DEBUG on
# so the suite can boot without a production secret. Explicit DEBUG still wins.
TESTING = 'pytest' in sys.modules

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=TESTING, cast=bool)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = resolve_secret_key(config('SECRET_KEY', default=''), debug=DEBUG)

ALLOWED_HOSTS = parse_allowed_hosts(
    config(
        'ALLOWED_HOSTS',
        default='localhost,127.0.0.1,bug-reporting-backend.herokuapp.com',
    ),
    debug=DEBUG,
)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',

    # Local apps
    'accounts',
    'projects',
    'issues',
    'comments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bug_tracking.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'bug_tracking.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'bug_tracking.exception_handler.custom_exception_handler',
    'DEFAULT_THROTTLE_RATES': {
        'login': '10/min',
        'register': '5/min',
        'refresh': '30/min',
        'password_reset': '5/min',
    },
}

# Simple JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    # Access tokens carry a hash of the password so a password change
    # invalidates tokens that have not expired yet.
    'CHECK_REVOKE_TOKEN': True,
}

# CORS Configuration. Credentials stay off because the SPA sends the JWT header.
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOWED_ORIGINS = parse_origins(
    config(
        'CORS_ALLOWED_ORIGINS',
        default=(
            'http://localhost:3000,http://127.0.0.1:3000,'
            'https://bug-reporting-system.vercel.app'
        ),
    )
)

CSRF_TRUSTED_ORIGINS = parse_origins(config('CSRF_TRUSTED_ORIGINS', default=''))
if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        origin for origin in CORS_ALLOWED_ORIGINS if origin.startswith('https://')
    ]

# Spectacular (Swagger) Configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'Bug Reporting System API',
    'DESCRIPTION': 'A comprehensive bug tracking API',
    'VERSION': '1.0.0',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
}

# dj-rest-auth Configuration. JWTs are returned in the response body for the SPA.
# Session login stays off so a cross-site form post cannot plant a session cookie.
REST_AUTH = {
    'USE_JWT': True,
    'SESSION_LOGIN': False,
    'JWT_AUTH_HTTPONLY': False,
    'JWT_AUTH_COOKIE': None,
    'JWT_AUTH_REFRESH_COOKIE': None,
    'USER_DETAILS_SERIALIZER': 'accounts.serializers.CustomUserDetailsSerializer',
    'LOGIN_SERIALIZER': 'accounts.serializers.EmailLoginSerializer',
    'OLD_PASSWORD_FIELD_ENABLED': True,
}

EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend',
)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='bugs@localhost')

if not DEBUG:
    _security = production_security_settings()
    SECURE_SSL_REDIRECT = config(
        'SECURE_SSL_REDIRECT',
        default=_security['SECURE_SSL_REDIRECT'],
        cast=bool,
    )
    SECURE_HSTS_SECONDS = _security['SECURE_HSTS_SECONDS']
    SECURE_HSTS_INCLUDE_SUBDOMAINS = _security['SECURE_HSTS_INCLUDE_SUBDOMAINS']
    SECURE_HSTS_PRELOAD = _security['SECURE_HSTS_PRELOAD']
    SECURE_PROXY_SSL_HEADER = _security['SECURE_PROXY_SSL_HEADER']
    SECURE_CONTENT_TYPE_NOSNIFF = _security['SECURE_CONTENT_TYPE_NOSNIFF']
    SECURE_REFERRER_POLICY = _security['SECURE_REFERRER_POLICY']
    SESSION_COOKIE_SECURE = _security['SESSION_COOKIE_SECURE']
    SESSION_COOKIE_HTTPONLY = _security['SESSION_COOKIE_HTTPONLY']
    SESSION_COOKIE_SAMESITE = _security['SESSION_COOKIE_SAMESITE']
    CSRF_COOKIE_SECURE = _security['CSRF_COOKIE_SECURE']
    CSRF_COOKIE_HTTPONLY = _security['CSRF_COOKIE_HTTPONLY']
    CSRF_COOKIE_SAMESITE = _security['CSRF_COOKIE_SAMESITE']
    X_FRAME_OPTIONS = _security['X_FRAME_OPTIONS']

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
