from django.core.exceptions import MiddlewareNotUsed
from django.core.management import call_command

class Minifier:
	def __init__(self):
		call_command('generate-minified-assets')
		print 'doit'
		raise MiddlewareNotUsed