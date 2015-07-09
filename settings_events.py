# Django settings for generic project.
import os
import sys

os.environ['LANG'] = 'en_US.UTF-8'

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
APP_FOLDER = os.path.join(PROJECT_FOLDER, 'apps')
INC_FOLDER = os.path.join(PROJECT_FOLDER, 'third-party')
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


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'core.context_processors.global_settings'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'core.middleware.SecureRequiredMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.middleware.UrlPatterns',
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
    'haystack',
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

TEMPL_FOLDER = os.path.join(PROJECT_FOLDER, 'templates')
TEMPLATE_DIRS = (TEMPL_FOLDER, )

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_FOLDER, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/events/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_FOLDER, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/events/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_FOLDER, 'static_files/static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

try:
    from settings_local_events import *
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        'Local settings file was not found. ' +
        'Ensure settings_local.py exists in project root.'
    )

if SEARCH_ENABLED:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'unify_events_haystack',
        },
    }
    # Enables updating of models with an associated SearchIndex
    # when that model is saved or deleted.
    HAYSTACK_SIGNAL_PROCESSOR = 'core.signals.CustomRealtimeSignalProcessor'
else:
    HAYSTACK_CONNECTIONS = {
        'default': {},
    }


# Settings for django-bleach, which sanitizes input from
# designated fields (i.e. wysiwyg editor content).
BLEACH_ALLOWED_TAGS = [
    'p',
    'br',
    'b',
    'i',
    'u',
    'em',
    'strong',
    'a',
    'ul',
    'ol',
    'li',
]
BLEACH_ALLOWED_ATTRIBUTES = ['href', 'title', 'style', 'alt']
BLEACH_ALLOWED_STYLES = ['font-weight', 'text-decoration']
BLEACH_STRIP_TAGS = True
BLEACH_STRIP_COMMENTS = True

# A custom list of elements whose markup and contents should be stripped
# completely from values from event descriptions modified by
# clean-unl-events-data.py (in apps/events/management/commands/).
# (Bleach strips tags, but keeps contents.)
BANNED_TAGS = ['style', 'script', 'link', 'noscript']

# Default description value for imported events with no description.
FALLBACK_EVENT_DESCRIPTION = 'No description provided.'

# Turn on/off HTML compression.
COMPRESS_HTML = True
