from django.db import models

# Create your models here.
class Base(models.Model):
	created  = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)	
	class Meta: abstract = True


class Profile(Base): pass


class Event(Base):
	#calendars  = ManyToMany relationship through CalendarEventRel w/Calendar
	title       = models.CharField(max_length=64)
	description = models.TextField(blank=True, null=True)
	instances   = models.ManyToManyField('EventInstance')


class EventInstance(Base):
	#events   = ManyToMany relationship w/Event
	start     = models.DateTimeField()
	end       = models.DateTimeField()


class Location(Base):
	"""User inputted locations that specify where an event takes place"""
	name        = models.CharField(max_length=128)
	description = models.TextField(blank=True, null=True)


class Calendar(Base):
	"""Calendar objects contain events that exist independent of the calendar,
	they may also subscribe to calendars which combine their owned events with
	events of other calendars."""
	name          = models.CharField(max_length=64)
	slug          = models.CharField(max_length=64, unique=True, blank=True)
	creator       = models.ForeignKey('auth.User', related_name='owned_calendars', null=True)
	editors       = models.ManyToManyField('auth.User', related_name='calendars')
	events        = models.ManyToManyField('Event', through='CalendarEventRel')
	subscriptions = models.ManyToManyField('Calendar', symmetrical=False, related_name="subscribers")
	
	@property
	def events_and_subs(self):
		"""Returns a queryset that combines this calendars events with its 
		subscribed events"""
		from django.db.models import Q
		qs = Event.objects.filter(
			Q(calendar=self) | Q(calendar__in=self.subscriptions.all())
		)
		return qs
	
	
	def create_event(self, **kwargs):
		"""Creates a new event using the keyword arguments provided and adds
		to the current calendar"""
		event = Event.objects.create(**kwargs)
		self.add_event(event)
	
	
	def add_event(self, event):
		"""Adds an existing event to the current calendar"""
		rel = CalendarEventRel(calendar=self, event=event)
		rel.save()
	
	
	def is_creator(self, user):
		"""Determine if user is creator of this calendar"""
		return user == self.creator
	
	
	def is_editor(self, user):
		"""Determine if user is member of editor set"""
		return user in self.editors
	
	
	def can_edit(self, user):
		"""Determine if user has permission to edit this calendar"""
		return self.is_creator(user) or self.is_editor(user)
	
	
	def save(self, *args, **kwargs):
		self.generate_slug()
		super(Calendar, self).save(*args, **kwargs)
	
	
	def generate_slug(self):
		"""Generates a slug from the calendar's name, ensuring that the slug
		is not already used by another calendar."""
		import re
		slug  = self.name.lower().replace(' ', '-')
		slug  = re.sub("[^A-Za-z1-9\s\-]", '', slug)
		
		count = 0
		while True:
			if not Calendar.objects.filter(slug=slug).count():
				break
			else:
				count += 1
				slug   = slug + '-' + str(count)
		self.slug = slug


class CalendarEventRel(Base):
	"""Defines the relations between calendars and events, as well as the event
	status for that calendar"""
	class Status:
		pending = 0
		posted  = 1
		choices = ((pending, 'pending'), (posted, 'posted'),)
	
	calendar = models.ForeignKey('Calendar')
	event    = models.ForeignKey('Event')
	state    = models.SmallIntegerField(choices=Status.choices, default=Status.pending)
	
