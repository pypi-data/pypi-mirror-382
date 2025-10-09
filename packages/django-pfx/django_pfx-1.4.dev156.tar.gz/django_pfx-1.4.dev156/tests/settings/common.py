import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.postgres',
    'pfx.pfxcore',
    'tests',
]

MIDDLEWARE = [
    'pfx.pfxcore.middleware.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'pfx.pfxcore.middleware.AuthenticationMiddleware',
    'pfx.pfxcore.middleware.CookieAuthenticationMiddleware',
]

USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French')]
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "tests/locale")]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'tests.User'

PFX_SECRET_KEY = "fake-secret-key"
PFX_COOKIE_DOMAIN = None

PFX_MAX_LIST_RESULT_SIZE = 0

ROOT_URLCONF = 'tests.urls'
APPEND_SLASH = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
PFX_RESET_PASSWORD_URL = (
    'http://localhost:8000/test?token={token}&uidb64={uidb64}')
PFX_SITE_NAME = 'Books Demo'

STORAGE_DEFAULT = 'pfx.pfxcore.storage.S3Storage'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    }
]

NH3_CONFIGS = {
    'default': {
        'tags': None,
        'attributes': None,
        'strip_comments': True,
        'url_schemes': None,
        'attribute_filter': None,
        'link_rel': None,
        'generic_attribute_prefixes': None,
        'tag_attribute_values': {},
        'set_tag_attribute_values': {},
    },
    'custom': {
        'tags': {'h1', 'p', 'span'},
        'attributes': {'*': {'class'}},
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_logger': False,
    'formatters': {
        'console': {
            'format': "\n%(name)-25s %(levelname)-8s %(message)s",
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
