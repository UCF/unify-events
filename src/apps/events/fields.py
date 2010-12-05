from django.db import models
from decimal   import Decimal

class CoordinatesField(models.Field):
	"""Stores coordinates of arbitrary number of dimensions."""
	
	description   = "Set of coordinates"
	__metaclass__ = models.SubfieldBase
	
	def __init__(self, *args, **kwargs):
		super(CoordinatesField, self).__init__(*args, **kwargs)
		
	
	def db_type(self, connection):
		return 'Coordinates'
	
	
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

