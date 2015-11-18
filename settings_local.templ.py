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
CANONICAL_ROOT = 'http://unify-events.smca.ucf.edu'

# Calendar Displayed on the Front Page
FRONT_PAGE_CALENDAR_PK = 1

# The first day of the week for month calendar generation.
# 0 is Monday, 6 is Sunday.
FIRST_DAY_OF_WEEK = 6

# Enables the search bar in the base template and sets up
# Haystack configuration. Turn off when debugging if
# Elasticsearch is not set up yet.
SEARCH_ENABLED = True

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
ILLEGAL_XML_CHARS = u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]'

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
