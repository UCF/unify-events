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

# AUTHENTICATION_BACKENDS = (
#     'events.auth.Backend',
#     'django.contrib.auth.backends.ModelBackend',
# )


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
    'django_bleach'
)

AUTH_PROFILE_MODULE = 'events.Profile'
FILE_UPLOAD_PATH = 'uploads'

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

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/events/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/events/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'static_files/static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

try:
    from settings_local import *
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        'Local settings file was not found. ' +
        'Ensure settings_local.py exists in project root.'
    )

TAGGIT_CASE_INSENSITIVE = True
