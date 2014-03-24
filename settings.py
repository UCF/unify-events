# Django settings for generic project.
import os
import sys

os.environ['LANG'] = 'en_US.UTF-8'

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
APP_FOLDER = os.path.join(PROJECT_FOLDER, 'apps')
INC_FOLDER = os.path.join(PROJECT_FOLDER, 'third-party')
ROOT_URLCONF = 'urls'
MINIFY = False

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


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'events.auth.Backend',
    'django.contrib.auth.backends.ModelBackend',
)


# Add local apps folder to python path
sys.path.append(APP_FOLDER)
sys.path.append(INC_FOLDER)

INSTALLED_APPS = (
    'core', # On top to lengthen the first and last name field for the user
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'profiles',
    'taggit',
    'events',
    'unlevents',
    'widget_tweaks',
    'django_bleach'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_true': {
            '()': 'logs.RequiredDebugTrue',
        },
        'require_debug_false': {
            '()': 'logs.RequiredDebugFalse',
        }
    },
    'formatters': {
        'talkative': {
            'format': '[%(asctime)s] %(levelname)s:%(module)s %(funcName)s %(lineno)d %(message)s'
        },
        'concise': {
            'format': '%(levelname)s: %(message)s (%(asctime)s)'
        }
    },
    'handlers': {
        'discard': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'talkative',
            'filters': ['require_debug_true']
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(PROJECT_FOLDER,'logs', 'application.log'),
            'formatter': 'concise',
            'filters': ['require_debug_false']
        }
    },
    'loggers': {
        'django': {
            'handlers': ['discard'],
            'propogate': True,
            'level': 'INFO'
        },
        'events': {
            'handlers': ['console', 'file'],
            'propogate': True,
            'level': 'DEBUG'
        },
        'util': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        }
    }
}

AUTH_PROFILE_MODULE = 'events.Profile'
FILE_UPLOAD_PATH = 'uploads'

DATABASE_ROUTERS = ['unlevents.dbrouter.UNLEventsRouter']

try:
    from settings_local import *
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        'Local settings file was not found. ' +
        'Ensure settings_local.py exists in project root.'
    )


TEMPLATE_DEBUG = DEBUG
TEMPL_FOLDER = os.path.join(PROJECT_FOLDER, 'templates')
MEDIA_ROOT = os.path.join(PROJECT_FOLDER, 'static')
TEMPLATE_DIRS = (TEMPL_FOLDER, )

STATIC_ROOT = ''
STATIC_URL = '/media/'

# Which HTML tags are allowed
BLEACH_ALLOWED_TAGS = [
    'p',
    'b',
    'i',
    'u',
    'em',
    'strong',
    'a',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'ul',
    'ol',
    'li',
    'blockquote'
]

# Which HTML attributes are allowed
BLEACH_ALLOWED_ATTRIBUTES = ['href', 'title', 'style', 'alt']

# Which CSS properties are allowed in 'style' attributes (assuming
# style is an allowed attribute)
BLEACH_ALLOWED_STYLES = ['font-weight', 'text-decoration']

# Strip unknown tags if True, replace with HTML escaped characters if
# False
BLEACH_STRIP_TAGS = True

# Strip comments, or leave them in.
BLEACH_STRIP_COMMENTS = True
