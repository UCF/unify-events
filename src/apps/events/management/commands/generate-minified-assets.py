import os

from django.core.management.base import BaseCommand
from django.core.management      import call_command
from django.conf                 import settings

def listdir_recursive(d):
	files = os.listdir(d)
	files = [(os.path.join(d, f)) for f in files]
	
	for f in files:
		if os.path.isdir(f):
			files.extend(listdir_recursive(f))
	return files


def extension_is(f, ext):
	return os.path.basename(f).split('.')[-1] == ext and os.path.isfile(f)


def minified(f):
	return 'min' in os.path.basename(f).split('.')


def minify(f, func):
	extension = os.path.basename(f).split('.')[-1]
	min_f     = f.replace('.' + extension, '.min.' + extension)
	
	with open(min_f, 'w') as write_handle:
		with open(f) as read_handle:
			contents = read_handle.read()
			minified = func(contents)
		write_handle.write(minified)
	return


class Command(BaseCommand):
	def handle(self, *args, **options):
		try:
			from cssmin import cssmin
		except ImportError:
			print 'This command relies on the cssmin python package'
			print '\t`easy_install cssmin`'
			return
		try:
			from jsmin import jsmin
		except ImportError:
			print 'This command relies on the jsmin python package'
			print '\t`easy_install jsmin`'
			return
		
		start_folder = settings.MEDIA_ROOT
		files = listdir_recursive(start_folder)
		
		css = filter(lambda f: extension_is(f, 'css') and not minified(f), files)
		js  = filter(lambda f: extension_is(f, 'js') and not minified(f), files)
		
		print 'Minifying css...',
		for f in css: minify(f, cssmin)
		print 'done'
		
		print 'Minifying js...',
		for f in js: minify(f, jsmin)
		print 'done'
		
		print 'Those files done got minifed...'