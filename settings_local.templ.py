THEME = 'default'
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = (
    #('Your Name', 'your_email@domain.com'),
)

# Determine if in Development mode. Used for things like ESIs.
DEV_MODE = False

LOGIN_URL = '/manager/login'
LOGOUT_URL = '/manager/logout'
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

# Calendar Displayed on the Front Page
FRONT_PAGE_CALENDAR_PK = 1

# How many days' worth of events should be displayed
# on the primary Calendar frontend view.
CALENDAR_MAIN_DAYS = 7

# The first day of the week for month calendar generation.
# 0 is Monday, 6 is Sunday.
FIRST_DAY_OF_WEEK = 6

# Enables the search bar in the base template and sets up
# Haystack configuration. Turn off when debugging if
# Elasticsearch is not set up yet.
SEARCH_ENABLED = True
