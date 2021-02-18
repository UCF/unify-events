class UNLEventsRouter(object):

	def db_for_read(self, model, **hints):
		if model._meta.app_label == 'unlevents':
			return 'unlevents'
		return None
	
	def db_for_write(self, model, **hints):
		return None # No writing to this db
	
	def allow_relations(self, obj1, obj2, **hints):
		if obj1._meta.app_label == 'unlevents' and obj2._meta.app_label == 'unlevents':
			return True
		return None
	
	def allow_syncdb(self, db, model):
		if db == 'unlevents' or model._meta.app_label == 'unlevents':
			return False
		return None