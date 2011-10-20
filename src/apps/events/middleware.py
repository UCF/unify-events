from django.core.exceptions import MiddlewareNotUsed
from django.core.management import call_command
from django.conf            import settings
import re

class Minifier:
	def __init__(self):
		settings.ORIGINAL_MEDIA_ROOT = settings.MEDIA_ROOT
		if settings.USE_MINIFY:
			call_command('generate-minified-assets')
			settings.MEDIA_ROOT = settings.MEDIA_ROOT + '/min'
			settings.MEDIA_URL  = settings.MEDIA_URL + 'min/'
		raise MiddlewareNotUsed