import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.postgres',
    'pfx.pfxcore',
    'tests_custom_user',
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
    os.path.join(BASE_DIR, "tests_custom_user/locale")]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'tests_custom_user.user'

PFX_SECRET_KEY = "fake-secret-key"
PFX_COOKIE_DOMAIN = None

PFX_MAX_LIST_RESULT_SIZE = 0

ROOT_URLCONF = 'tests_custom_user.urls'
APPEND_SLASH = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
PFX_RESET_PASSWORD_URL = (
    'http://localhost:8000/test?token={token}&uidb64={uidb64}')
PFX_SITE_NAME = 'Books Demo'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    }
]

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
