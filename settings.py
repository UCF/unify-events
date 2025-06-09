# Django settings for generic project.
import os
import sys


try:
    from app_version import APP_VERSION
except ImportError:
    pass

os.environ['LANG'] = 'en_US.UTF-8'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_FOLDER = os.path.join(BASE_DIR, 'apps')
INC_FOLDER = os.path.join(BASE_DIR, 'third-party')
ROOT_URLCONF = 'urls'

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

TIME_ZONE = 'America/New_York'
DATE_INPUT_FORMATS = ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y', '%b %d %Y',
'%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y',
'%B %d, %Y', '%d %B %Y', '%d %B, %Y')
TIME_INPUT_FORMATS = ('%I:%M %p', '%H:%M:%S')
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'core.middleware.SecureRequiredMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.middleware.CorsRegex',
    'core.middleware.MinifyHTMLMiddleware',
)

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


WSGI_APPLICATION = 'wsgi.application'

INSTALLED_APPS = (
    'core', # On top to lengthen the first and last name field for the user
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_saml2_auth',
    'profiles',
    'taggit',
    'events',
    'unlevents',
    'widget_tweaks',
    'django_bleach',
    'storages'
)

AUTH_PROFILE_MODULE = 'events.Profile'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATABASE_ROUTERS = ['unlevents.dbrouter.UNLEventsRouter']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.global_settings'
            ],
        },
    },
]

try:
    from settings_local import *
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        'Local settings file was not found. ' +
        'Ensure settings_local.py exists in project root.'
    )

TAGGIT_CASE_INSENSITIVE = True
