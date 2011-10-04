THEME = 'default'

DEBUG          = True

ADMINS         = (
	#('Your Name', 'your_email@domain.com'),
)


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
STATIC_URL = '/static/'

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
		'NAME'    : '',
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
LDAP_NET_HOST    = 'net.ucf.edu'
LDAP_NET_PORT    = 389 #636
LDAP_NET_VERSION = 2
LDAP_NET_BASE_DN = 'dc=net,dc=ucf,dc=edu'