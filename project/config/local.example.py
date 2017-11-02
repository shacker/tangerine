from .settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tangerine',
        'USER': 'you',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '',
    },
}

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

SECRET_KEY = 'sdf0suoijfksdfsdf2rl2km*st6*&*9sdf'

EMAIL_PORT = 1025
EMAIL_HOST = 'localhost'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Uncomment to test production asset compilation locally (should rarely be needed), then run `./manage.py compress`
# COMPRESS_OFFLINE = True
# COMPRESS_ENABLED = True
