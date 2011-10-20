THEME  = 'default'
DEBUG  = True
ADMINS = (
	#('Your Name', 'your_email@domain.com'),
)

LOGIN_URL           = '/manager/login'
LOGOUT_URL          = '/manager/logout'
LOGIN_REDIRECT_URL  = '/manager/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'whatisthisnonsense?'

DATABASES = {
	'default': {
		# postgresql_psycopg2, postgresql, mysql, sqlite3, oracle
		'ENGINE'  : 'django.db.backends.sqlite3',
		# Or path to database file if using sqlite3.
		'NAME'    : 'events.db',
		# Not used with sqlite3.
		'USER'    : '',
		# Not used with sqlite3.
		'PASSWORD': '',
		# Set to empty string for localhost. Not used with sqlite3.
		'HOST'    : '',
		# Set to empty string for default. Not used with sqlite3.
		'PORT'    : '',
	}
}

# NET Domain LDAP CONFIG
LDAP_NET_HOST        = 'ldaps://net.ucf.edu'
LDAP_NET_BASE_DN     = 'ou=People,dc=net,dc=ucf,dc=edu'
LDAP_NET_USER_SUFFIX = '@net.ucf.edu'
LDAP_NET_ATTR_MAP    = { # LDAP Object -> User Object
  'givenName':'first_name',
  'sn'       :'sn',
  'mail'     :'email'
}
LDAP_NET_SEARCH_USER  = ''
LDAP_NET_SEARCH_PASS = ''

# Calendar Displayed on the Front Page
FRONT_PAGE_CALENDAR_SLUG = ''

# Minify JS and CSS. Requires some Apache config modifications
USE_MINIFY = True