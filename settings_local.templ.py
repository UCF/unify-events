THEME = 'default'
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['unify-events.smca.ucf.edu']
USE_X_FORWARDED_HOST = True

ADMINS = (
    #('Your Name', 'your_email@domain.com'),
)

# Determine if in Development mode. Used for things like ESIs.
DEV_MODE = False

LOGIN_URL = '/manager/login/'
LOGOUT_URL = '/manager/logout/'
LOGIN_REDIRECT_URL = '/manager/'

# Make this unique, and don't share it with anybody.
# http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = '**************************************************'

DATABASES = {
    'default': {
        # postgresql_psycopg2, postgresql, mysql, sqlite3, oracle
        'ENGINE': 'django.db.backends.sqlite3',
        # Or path to database file if using sqlite3.
        'NAME': 'events.db',
        # Not used with sqlite3.
        'USER': '',
        # Not used with sqlite3.
        'PASSWORD': '',
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '',
    },
    # 'unlevents': {
    #     # postgresql_psycopg2, postgresql, mysql, sqlite3, oracle
    #     'ENGINE': 'django.db.backends.mysql',
    #     # Or path to database file if using sqlite3.
    #     'NAME': '',
    #     # Not used with sqlite3.
    #     'USER': '',
    #     # Not used with sqlite3.
    #     'PASSWORD': '',
    #     # Set to empty string for localhost. Not used with sqlite3.
    #     'HOST': '',
    #     # Set to empty string for default. Not used with sqlite3.
    #     'PORT': '',
    # }
}

# NET Domain LDAP CONFIG
LDAP_NET_HOST = 'ldaps://net.ucf.edu'
LDAP_NET_BASE_DN = 'ou=People,dc=net,dc=ucf,dc=edu'
LDAP_NET_USER_SUFFIX = '@net.ucf.edu'
LDAP_NET_ATTR_MAP = { # LDAP Object -> User Object
    'givenName': 'first_name',
    'sn': 'sn',
    'mail': 'email'
}
LDAP_NET_SEARCH_USER = ''
LDAP_NET_SEARCH_PASS = ''
LDAP_NET_SEARCH_SIZELIMIT = 5

# Limit the user search results to 5 people
USER_SEARCHLIMIT = 5

# Root path by which canonical urls are built. Include protocol. Do not include trailing slash.
CANONICAL_ROOT = 'https://events.ucf.edu'

# Calendar Displayed on the Front Page
FRONT_PAGE_CALENDAR_PK = 1

# The first day of the week for month calendar generation.
# 0 is Monday, 6 is Sunday.
FIRST_DAY_OF_WEEK = 6

# The number of calendar results displayed on the search
CALENDAR_RESULTS_LIMIT = 10

# Domain name of map service. Update this value to DEV/QA environments when appropriate.
MAPS_DOMAIN = 'map.ucf.edu'

# Path of location data json feed (for importer.)  Uses MAP_DOMAIN as the domain name.
LOCATION_DATA_URL = '/locations.json?types=building,regionalcampus,parkinglot'

# Google Analytics tracking ID
GA_ACCOUNT = ''

# Google Webmaster Tools verification code (copy from the provided HTML meta tag)
GOOGLE_WEBMASTER_VERIFICATION = ''

# Secure HTTPS / SSL
HTTPS_SUPPORT = True
SECURE_REQUIRED_PATHS = [
    '/manager/',
    '/admin/',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = HTTPS_SUPPORT
CSRF_COOKIE_SECURE = HTTPS_SUPPORT


# Enable cache clearing functionality. Turn off when running data imports.
ENABLE_CLEARCACHE = True
VARNISH_NODES = []

# Settings for django-bleach, which sanitizes input from
# designated fields (i.e. wysiwyg editor content).
BLEACH_ALLOWED_TAGS = [
    'p',
    'span',
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
BLEACH_ALLOWED_ATTRIBUTES = ['href', 'title', 'style', 'alt', 'target']
BLEACH_ALLOWED_STYLES = ['font-weight', 'text-decoration']
BLEACH_STRIP_TAGS = True
BLEACH_STRIP_COMMENTS = True

# Illegal characters for xml
ILLEGAL_XML_CHARS = '[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]'

# A custom list of elements whose markup and contents should be stripped
# completely from values from event descriptions modified by
# clean-unl-events-data.py (in apps/events/management/commands/).
# (Bleach strips tags, but keeps contents.)
BANNED_TAGS = ['style', 'script', 'link', 'noscript']

# Default description value for imported events with no description.
FALLBACK_EVENT_DESCRIPTION = 'No description provided.'

# Turn on/off HTML compression.
COMPRESS_HTML = True

# Specify views that require CORS-friendly response headers.
CORS_REGEX = '.*feed\.(json|xml|rss)'
CORS_GET_PARAMS = {
    'is_widget': 'true|True',
    'format': 'rss|xml|json'
}

# Used to determine if a calendar is
# active or not. If the calendar does not
# have any events with a start time greater
# than datetime.now() - the number of days below
# it is considered expired.
CALENDAR_EXPIRATION_DAYS = 365

# List of disallowed calendar names
# Note: Enter new names all lower case
DISALLOWED_CALENDAR_TITLES = [
    'events at ucf',
    'events',
    'ucf events'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
    	'standard': {
        	'format': '[%(asctime)s] %(levelname)s:%(module)s %(funcName)s %(lineno)d %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(BASE_DIR, 'logs/application.log'),
            'maxBytes': 1024*1024*5, # 5 MB
        	'backupCount': 5,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}

USE_SAML = False

# SSO Settings
SAML2_AUTH = {
    # Required setting
    'SAML_CLIENT_SETTINGS': { # Pysaml2 Saml client settings (https://pysaml2.readthedocs.io/en/latest/howto/config.html)
        'entityid': '{entity_id}', # The optional entity ID string to be passed in the 'Issuer' element of authn request, if required by the IDP.
        'metadata': {
            'remote': [
                {
                    "url": '{metadata_url}', # The auto(dynamic) metadata configuration URL of SAML2
                },
            ],
        },
    },

    # Optional settings below
    'DEFAULT_NEXT_URL': '/admin',  # Custom target redirect URL after the user get logged in. Default to /admin if not set. This setting will be overwritten if you have parameter ?next= specificed in the login URL.
    'NEW_USER_PROFILE': {
        'USER_GROUPS': [],  # The default group name when a new user logs in
        'ACTIVE_STATUS': True,  # The default active status for new users
        'STAFF_STATUS': False,  # The staff status for new users
        'SUPERUSER_STATUS': False,  # The superuser status for new users
    },
    'ATTRIBUTES_MAP': {
        'email': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
        'username': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/NID',
        'first_name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname',
        'last_name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname',
        'token': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',  # Mandatory, can be unrequired if TOKEN_REQUIRED is False
        'groups': 'search_service_security_groups',  # Optional
    },
    'TRIGGER': {
        'CREATE_USER': 'core.saml_hooks.on_saml_user_create',
        'BEFORE_LOGIN': 'core.saml_hooks.on_saml_before_login',
    },
    'ASSERTION_URL': '{assertion_url}', # Custom URL to validate incoming SAML requests against
}
