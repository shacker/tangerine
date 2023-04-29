import base64
import os
from pathlib import Path

from goodconf import GoodConf, Field

# Make this the same as in main settings:
BASE_DIR = Path(__file__).resolve().parent.parent


class AppConfig(GoodConf):
    """Configuration for template site. Pulls environment variables from
    the running instance and stores them as Django settings for use in code."""

    ALLOWED_HOSTS = Field(default=["*"])
    AWS_S3_REGION_NAME = Field(default="us-west-2")
    AWS_LOCATION = Field(default="", help="Var used by Django to prepend bucket prefix")
    PRIVATE_S3_BUCKET_PREFIX = Field(default="", help="Bucket prefix for this server instance")
    AWS_SUBMITFILES_BUCKET_NAME = Field(default="", help="Connection to S3 bucket for media")
    DEBUG = Field(default=False, help="Toggle debugging.")
    EMAIL_BACKEND = Field(default="django.core.mail.backends.console.EmailBackend")
    ENVIRONMENT = Field(default="", help="Environment where application is deployed.")
    LOCAL_DEV = Field(default=False, help="Enable local development tools")
    LOG_LEVEL = Field(default="INFO", help="Log level for application")
    DATABASE_URL = Field(
        default="postgres://localhost:5432/apppack-template", help="Database connection."
    )
    MEDIA_ROOT = Field(default=str(BASE_DIR / "media"))
    STATIC_ROOT = Field(default=str(BASE_DIR / "staticfiles"))
    PRIVATE_S3_BUCKET_NAME = Field(default="", help="Connection to S3 private bucket for media")
    REDIS_ENABLED = Field(default=False, help="If False, db caching will be used.")
    REDIS_URL = Field(default="redis://127.0.0.1:6379")
    REDIS_PREFIX = Field(default="blog")
    SECRET_KEY: str = Field(
        initial=lambda: base64.b64encode(os.urandom(60)).decode(),
        description="Used for cryptographic signing. "
        "https://docs.djangoproject.com/en/2.0/ref/settings/#secret-key",
    )
    SENTRY_DSN = Field(default="")
    TEST_EMAIL_TO = Field(default="")

    class Config:
        # Load env vars from file `ap_template.yml`
        default_files = ["blog/config/local.yml", "blog/config/local.json"]


config = AppConfig()


def manage_py():
    """Entrypoint for manage.py"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog.config.settings")
    config.django_manage()


def generate_config():
    """Entrypoint for dumping out sample config"""
    print(config.generate_json(LOCAL_DEV=True, DEBUG=True, LOG_LEVEL="DEBUG"))
