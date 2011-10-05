# Django settings for generic project.
import os
import sys

# This import is up here to allow THEME
# to affect the template folder path
try:
	from settings_local import *
except ImportError:
	from django.core.exceptions import ImproperlyConfigured
	raise ImproperlyConfigured(
		'Local settings file was not found. ' +
		'Ensure settings_local.py exists in project root.'
	)

MANAGERS       = ADMINS
TEMPLATE_DEBUG = DEBUG

PROJECT_FOLDER    = os.path.dirname(os.path.abspath(__file__))
APP_FOLDER        = os.path.join(PROJECT_FOLDER, 'apps')
INC_FOLDER        = os.path.join(PROJECT_FOLDER, 'third-party')
TEMPL_FOLDER      = os.path.join(PROJECT_FOLDER, 'themes', THEME, 'templates')
ROOT_URLCONF      = os.path.basename(PROJECT_FOLDER) + '.urls'
MEDIA_ROOT        = os.path.join(PROJECT_FOLDER, 'themes', THEME, 'static')

LOGIN_URL         = 'login'
LOGOUT_URL        = 'logout'

TIME_ZONE         = 'America/New_York'
LANGUAGE_CODE     = 'en-us'
SITE_ID           = 1
USE_I18N          = False


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = STATIC_URL


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
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
)

AUTHENTICATION_BACKENDS = (
	'events.auth.Backend',
)

TEMPLATE_DIRS = (TEMPL_FOLDER,)

# Add local apps folder to python path
sys.path.append(APP_FOLDER)
sys.path.append(INC_FOLDER)
INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'events',
	'messages',
)

LOGGING = {
	'version':1,
	'disable_existing_loggers':True,
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
			'format':'%(levelname)s: %(asctime)s %(module)s %(funcName)s %(message)s'
		},
		'concise': {
			'format':'%(levelname)s: %(message)s (%(asctime)s)'
		}
	},
	'handlers': {
		'discard': {
			'level':'DEBUG',
			'class':'django.utils.log.NullHandler'
		},
		'console': {
			'level':'DEBUG',
			'class':'logging.StreamHandler',
			'formatter':'concise',
			'filters': ['require_debug_true']
		},
		'file': {
			'level': 'INFO',
			'class':'logging.FileHandler',
			'filename':'logs/application.log',
			'formatter':'concise',
			'filters': ['require_debug_false']
		}
	},
	'loggers': {
		'django': {
			'handlers':['discard'],
			'propogate': True,
			'level':'INFO'
		},
		'events.auth': {
			'handlers':['console', 'file'],
			'level':'DEBUG'
		},
		'views': {
			'handlers':['console', 'file'],
			'level':'DEBUG'
		}
	}
}

