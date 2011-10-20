import os

from threading                   import Thread
from django.core.management.base import BaseCommand
from django.core.management      import call_command
from django.conf                 import settings
from shutil                      import rmtree, copytree

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
	with open(f, 'r') as read_handle:
		contents = read_handle.read()
		minified = func(contents)
	
	with open(f, 'w') as write_handle:
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
		
		from_folder = os.path.abspath(settings.ORIGINAL_MEDIA_ROOT)
		to_folder   = from_folder + '-min'
		
		if os.path.isdir(to_folder):
			try:
				rmtree(to_folder)
			except Exception as e:
				print 'Unable to remove previously existing minified folder, reason:\n\t', e
				return
		
		try:
			copytree(from_folder, to_folder)
		except Exception as e:
			print 'Unable to create minified assets folder, reason:\n\t', e
			return
		
		files = listdir_recursive(to_folder)
		
		css = set(filter(lambda f: extension_is(f, 'css') and not minified(f), files))
		js  = set(filter(lambda f: extension_is(f, 'js') and not minified(f), files))
		
		print 'Minifying css and js...',
		def css_min():
			for f in css:
				minify(f, cssmin)
		css_thread = Thread(target=css_min)
		css_thread.start()
		
		def js_min():
			for f in js:
				minify(f, jsmin)
		js_thread = Thread(target=js_min)
		js_thread.start()
		
		css_thread.join()
		js_thread.join()
		print 'done'