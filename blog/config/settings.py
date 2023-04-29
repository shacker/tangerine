from pathlib import Path
from django.contrib.messages import constants as message_constants
import dj_database_url
import os

# Load secrets from ENV VARS or local json/yml and hoist them into django settings
from .config import config

config.load()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Overridden on server instances by S3 config below
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = config.MEDIA_ROOT
MEDIA_URL = "/media/"


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.DEBUG
IS_PROD = config.ENVIRONMENT == "production"


ALLOWED_HOSTS = config.ALLOWED_HOSTS


DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_extensions",
]

LOCAL_APPS = [
    "blog.tangerine",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Default integer type for auto-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


ROOT_URLCONF = "blog.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [f"{BASE_DIR}/templates"],
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

WSGI_APPLICATION = "blog.config.wsgi.application"


DATABASES = {"default": dj_database_url.parse(config.DATABASE_URL)}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
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

# Override CSS class for the ERROR tag level to match Bootstrap class name
MESSAGE_TAGS = {message_constants.ERROR: "danger"}


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = "/static/"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = config.STATIC_ROOT


# MEDIA
if config.PRIVATE_S3_BUCKET_NAME:
    # Use Amazon S3 for storage for uploaded media files
    # Keep them private by default
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    # Amazon S3 settings.
    AWS_STORAGE_BUCKET_NAME = config.PRIVATE_S3_BUCKET_NAME
    AWS_LOCATION = config.PRIVATE_S3_BUCKET_PREFIX
    AWS_SUBMITFILES_BUCKET_NAME = config.AWS_SUBMITFILES_BUCKET_NAME
    AWS_S3_REGION_NAME = config.AWS_S3_REGION_NAME
    AWS_AUTO_CREATE_BUCKET = False
    AWS_HEADERS = {"Cache-Control": "public, max-age=86400"}
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = "private"
    AWS_QUERYSTING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 604800  # One week expiration on signed S3 URLs
    AWS_S3_SECURE_URLS = True
    AWS_REDUCED_REDUNDANCY = False
    AWS_IS_GZIPPED = False

    MEDIA_ROOT = "/"
    MEDIA_URL = "https://s3.{}.amazonaws.com/{}/".format(
        AWS_S3_REGION_NAME, AWS_STORAGE_BUCKET_NAME
    )
else:
    MEDIA_ROOT = config.MEDIA_ROOT
    MEDIA_URL = "/media/"
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "account_login"


# Use Redis caching if enabled for this project; else db caching
REDIS_ENABLED = config.REDIS_ENABLED
if REDIS_ENABLED:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"{config.REDIS_URL}/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": False,
            },
            "KEY_PREFIX": config.REDIS_PREFIX,
            "TIMEOUT": 60 * 60 * 24 * 30,  # 30 days
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }


ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = None

# Email
DEFAULT_FROM_EMAIL = "proj1-noreply@energy-solution.com"
SERVER_EMAIL = "proj1-noreply@energy-solution.com"
AWS_SES_AUTO_THROTTLE = None
AWS_SES_REGION_NAME = config.AWS_S3_REGION_NAME
AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"


if config.EMAIL_BACKEND:
    EMAIL_BACKEND = config.EMAIL_BACKEND

# If we're on production, overwrite to use live email
if IS_PROD:
    EMAIL_BACKEND = "django_ses.SESBackend"

TEST_EMAIL_TO = config.TEST_EMAIL_TO

#  Prevents Javascript clients from accessing csrf tokens
CSRF_COOKIE_HTTPONLY = True

# Ensure cookies get a `secure` header per SOC requirements.
# Breaks local login if True on localhost!
SESSION_COOKIE_SECURE = False if DEBUG else True
