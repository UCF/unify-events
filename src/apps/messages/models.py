from django.db import models
from fields    import *

# Generic relationships
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes        import generic

class Message(models.Model):
	"""Object to object messaging."""
	sender   = generic.GenericForeignKey('s_type', 's_id')
	s_id     = models.PositiveIntegerField(null=True)
	s_type   = models.ForeignKey(ContentType, related_name='messages_sent', null=True)
	
	receiver = generic.GenericForeignKey('r_type', 'r_id')
	r_id     = models.PositiveIntegerField(null=True)
	r_type   = models.ForeignKey(ContentType, related_name='messages_received', null=True)
	
	content  = models.TextField()
	created  = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.content
	
	
	def __unicode__(self):
		return unicode(self.__str__())
	
	
	def __repr__(self):
		return self.id
	
	
	def __init__(self, *args, **kwargs):
		super(Message, self).__init__(*args, **kwargs)
		
