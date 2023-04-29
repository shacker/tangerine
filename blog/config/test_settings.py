"""
Settings and variables specific to the test runner.
"""
import os
from .settings import *  # noqa

import dj_database_url

if "DATABASE_URL" in os.environ:
    DATABASES = {"default": dj_database_url.config()}

# DEBUG
# ------------------------------------------------------------------------------
# Turn debug off so tests run faster
DEBUG = False
TEMPLATES[0]["OPTIONS"]["debug"] = False  # noqa: F405

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = "CHANGEME!!!"

# Mail settings
# ------------------------------------------------------------------------------
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025

# In-memory email backend stores messages in django.core.mail.outbox
# for unit testing purposes
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Affects futures.concurrency only. Override the main settings to prevent
# requests from being executed out of order in VCR recordings.
CONCURRENT_MAX_WORKERS = 1


# CACHING
# ------------------------------------------------------------------------------
# Speed advantages of in-memory caching without having to run Memcached.
# Commented out to ensure we are testing against actual redis backemnd from main settings.
# CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

CACHEOPS_ENABLED = False

# File Storage
# ------------------------------------------------------------------------------
# Instead of having to deal with S3/boto for dynamically spun up test envs, use local file store in tests
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = "django.test.runner.DiscoverRunner"


# PASSWORD HASHING
# ------------------------------------------------------------------------------
# Use fast password hasher so tests run faster
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
