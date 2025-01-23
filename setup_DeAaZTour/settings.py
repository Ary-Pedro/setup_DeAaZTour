from pathlib import Path
from django.contrib.messages import constants as messages
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
# criar env para a secret key
SECRET_KEY ='django-insecure-k%es*+c3f0tws+hez6w)%kgcq*0s7rg2=4354c$1s9eb$wh9aa'
DEBUG = True
ALLOWED_HOSTS = ['*']

# python manage.py compress

#DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
#ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*')
#SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-k%es*+c3f0tws+hez6w)%kgcq*0s7rg2=4354c$1s9eb$wh9aa')

# Application definition
# Adicionar?!
# "crispy_forms" 
# "crispy_bootstrap5"
BASE_INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MY_APPS = [
    "apps.worker",
    "apps.agency",
    "apps.service",
    "apps.client",
]

FUNCIONAIS_APPS = [
    "phonenumber_field",
    'compressor',
    "crispy_forms",
    "crispy_bootstrap5",
]

INSTALLED_APPS = BASE_INSTALLED_APPS + MY_APPS + FUNCIONAIS_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = "setup_DeAaZTour.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "setup_DeAaZTour.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static_global",
]
STATIC_ROOT = BASE_DIR / "static_root"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# Django Compressor settings
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# Django bootstrap5 settings
RISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Whitenoise settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Authentication settings
AUTH_USER_MODEL = "worker.Funcionario"

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'recuperarsenhadeaaztur@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'gask herz xqlr kdmq')
DEFAULT_FROM_EMAIL = "recuperarsenhadeaaztur@gmail.com"

# Base URL for the project
BASE_URL = "http://localhost:8000"

# Message tags
MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}
"""
# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security settings for deployment
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'True') == 'True'
SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_SECURE_HSTS_SECONDS', 3600))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True') == 'True'
SECURE_HSTS_PRELOAD = os.getenv('DJANGO_SECURE_HSTS_PRELOAD', 'True') == 'True'
"""
'''
# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}'''