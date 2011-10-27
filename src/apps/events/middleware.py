from django.core.exceptions import MiddlewareNotUsed
from django.core.management import call_command
from django.conf            import settings
import re

class Minifier:
	active = False
	
	def __init__(self):
		if settings.MINIFY and not Minifier.active:
			call_command('generate-minified-assets')
			Minifier.active     = True
			settings.MEDIA_URL  = settings.MEDIA_URL + 'min/'
			settings.MEDIA_ROOT = settings.MEDIA_ROOT + '/min'
			
		raise MiddlewareNotUsed