from django.db import models
from decimal   import Decimal

def error(m):
	import logging
	logging.info(m)


class ImageField(models.ImageField):
	pass


class CoordinatesField(models.Field):
	"""Stores coordinates of arbitrary number of dimensions."""
	
	description   = "Set of coordinates"
	__metaclass__ = models.SubfieldBase
	
	def __init__(self, *args, **kwargs):
		super(CoordinatesField, self).__init__(*args, **kwargs)
		
	
	def db_type(self, connection):
		return 'varchar(32)'
	
	
	def get_internal_type(self):
		return 'CharField'
	
	
	def to_python(self, value):
		if value is None:
			return value
		
		if getattr(value, '__iter__', False):
			return list(value)
		
		value = value.strip(' ][')
		return [float(i) for i in value.split(',')]
	
	
	def get_prep_value(self, value):
		if value is None: value
		
		value = [str(i) for i in value]
		
		return ','.join(value)


class SettingsField(models.Field):
	"""Stores arbitrary simple key-value pairings presented as a python 
	dictionary."""
	description   = "Settings Field"
	__metaclass__ = models.SubfieldBase
	
	"""docstring for SettingsField"""
	def __init__(self, *args, **kwargs):
		super(SettingsField, self).__init__(*args, **kwargs)
	
	
	def get_internal_type(self):
		return 'TextField'
	
	
	def to_python(self, value):
		if isinstance(value, dict().__class__):
			return value
		
		
		if isinstance(value, str().__class__) or\
			isinstance(value, unicode().__class__):
			import json
			try:
				value = json.loads(value)
			except ValueError:
				error('Settings string could not be parsed as JSON')
				value = {}
			return value
		
		return {}
	
	
	def get_prep_value(self, value):
		import json
		return json.dumps(value)
		