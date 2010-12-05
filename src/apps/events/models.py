from django.db      import models
from django.contrib import auth
from functions      import sluggify

# Create your models here.
class Base(models.Model):
	created  = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)	
	class Meta: abstract = True


class Profile(Base):
	#user = One to One with User
	pass


class User(auth.models.User):
	#owned_calendars  = One to Many with Calendar
	#edited_calendars = One to Many with Calendar
	profile = models.OneToOneField('Profile', related_name='user', null=True, blank=True)
	
	def create_calendar(self, **kwargs):
		calendar = Calendar.objects.create(**kwargs)
		self.add_calendar(calendar)
		return calendar
	
	
	def add_calendar(self, calendar):
		self.owned_calendars.add(calendar)
	
	
	@property
	def calendars(self):
		return list(self.owned_calendars.all()) + list(self.edited_calendars.all())


class Event(Base):
	"""This object provides the link between the time and places events are to
	take place and the purpose and name of the event as well as the calendard to
	which the events belong."""
	class Status:
		pending = 0
		posted  = 1
		choices = ((pending, 'pending'), (posted, 'posted'),)
	
	#instances  = One to Many relationship with EventInstance
	calendar    = models.ForeignKey('Calendar', related_name='events')
	state       = models.SmallIntegerField(choices=Status.choices, default=Status.pending)
	title       = models.CharField(max_length=64)
	description = models.TextField(blank=True, null=True)
	
	@property
	def slug(self):
		return sluggify(self.title)
	
	
	def __str__(self):
		return self.title
	
	
	def __unicode__(self):
		return unicode(self.title)
	
	
	def __repr__(self):
		return str(self.calendar) + '/' + self.title


class EventInstance(Base):
	"""Object which describes the time and place that an event is occurring"""
	class Recurs:
		daily, weekly, biweekly, monthly, yearly = range(0,5)
		choices = (
			('daily'    , daily),
			('weekly'   , weekly),
			('biweekly' , biweekly),
			('monthly'  , monthly),
			('yearly'   , yearly),
		)
		
		
		@classmethod
		def next_monthly_date(cls, d):
			"""Next date in recurring by month series from datetime d"""
			from datetime import datetime
			m = d.date().month
			if m != 12: m += 1
			else      : m  = 1
			return d.replace(month=m)
		
		
		@classmethod
		def next_yearly_date(cls, d):
			"""Next date in recurring by year series from datetime d"""
			from datetime import datetime
			y = d.date().year
			return d.replace(year=y+1)
		
		
		@classmethod
		def next_arbitrary_date(cls, d, delta):
			"""Next date in recurring by delta days from datetime d"""
			from datetime import timedelta
			delta = timedelta(days=delta)
			return d + delta
		
		
		@classmethod
		def next_date(cls, d, i):
			"""Given a datetime d, and Recurring interval i (Recurring.daily,
			Recurring.weekly, etc), will return the next date in the series"""
			next = {
				cls.daily   : lambda: cls.next_arbitrary_date(d, 1),
				cls.weekly  : lambda: cls.next_arbitrary_date(d, 7),
				cls.biweekly: lambda: cls.next_arbitrary_date(d, 14),
				cls.monthly : lambda: cls.next_monthly_date(d),
				cls.yearly  : lambda: cls.next_yearly_date(d),
			}.get(i, lambda: None)()
			
			if next is None:
				raise ValueError('Invalid constant provided for interval type')
			
			return next
	
	#children = One To Many relationship with EventInstances
	event     = models.ForeignKey('Event', related_name='instances')
	location  = models.ForeignKey('Location', related_name='events', null=True, blank=True)
	start     = models.DateTimeField()
	end       = models.DateTimeField()
	interval  = models.SmallIntegerField(null=True, blank=True, choices=Recurs.choices)
	limit     = models.PositiveSmallIntegerField(null=True, blank=True)
	parent    = models.ForeignKey('EventInstance', related_name='children', null=True, blank=True)
	
	def save(self, *args, **kwargs):
		try:
			#If we can find an object that matches this one, no update is needed
			EventInstance.objects.get(
				pk=self.pk,
				start=self.start,
				end=self.end,
				location=self.location,
				interval=self.interval,
				limit=self.limit
			)
			update = False
		except EventInstance.DoesNotExist:
			#Otherwise it's the first save or something has changed, update
			update = True
		
		super(EventInstance, self).save(*args, **kwargs)
		if update:
			self.update_children()
	
	
	def update_children(self):
		"""Will verify that all children of this event exist and are valid if
		the instance is recurring."""
		self.children.all().delete()
		if self.limit is None or self.interval is None: return
		
		limit    = self.limit - 1
		instance = self
		
		while limit > 0:
			delta    = instance.end - instance.start
			nstart   = EventInstance.Recurs.next_date(instance.start, self.interval)
			nend     = nstart + delta
			instance = self.children.create(
				event=instance.event,
				start=nstart,
				end=nend,
				location=self.location
			)
			limit -= 1
	
	
	def delete(self, *args, **kwargs):
		self.children.all().delete()
		super(EventInstance, self).delete(*args, **kwargs)
	
	
	def __repr__(self):
		return str(self.start)


class Location(Base):
	"""User inputted locations that specify where an event takes place"""
	#events     = One to Many relationship with EventInstance
	name        = models.CharField(max_length=128)
	description = models.TextField(blank=True, null=True)


class Calendar(Base):
	"""Calendar objects contain events that exist independent of the calendar,
	they may also subscribe to calendars which combine their owned events with
	events of other calendars."""
	#events       = One to Many relationship with Event
	name          = models.CharField(max_length=64)
	slug          = models.CharField(max_length=64, unique=True, blank=True)
	creator       = models.ForeignKey('User', related_name='owned_calendars', null=True)
	editors       = models.ManyToManyField('User', related_name='edited_calendars')
	subscriptions = models.ManyToManyField('Calendar', symmetrical=False, related_name="subscribers")
	
	@property
	def events_and_subs(self):
		"""Returns a queryset that combines this calendars event instances with
		its subscribed event instances"""
		from django.db.models import Q
		qs = EventInstance.objects.filter(
			Q(event__calendar=self) | Q(event__calendar__in=self.subscriptions.all())
		)
		return qs
	
	
	@property
	def event_instances(self):
		qs = EventInstance.objects.filter(event__calendar=self)
		return qs
	
	
	def find_event_instances(self, start, end):
		from django.db.models import Q
		qs = self.events_and_subs.filter(
			Q(end__gte=start) & Q(end__lte=end) |
			Q(start__gte=start) & Q(start__lte=end)
		)
		return qs
	
	
	def subscribe(self, *args):
		"""Subscribe to provided calendars"""
		self.subscriptions.add(*args)
	
	
	def unsubscribe(self, *args):
		"""Unsubscribe from provided calendars"""
		self.subscriptions.remove(*args)
	
	
	def create_event(self, **kwargs):
		"""Creates a new event using the keyword arguments provided and adds
		to the current calendar"""
		event = Event.objects.create(calendar=self, **kwargs)
		self.add_event(event)
		return event
	
	
	def add_event(self, event):
		"""Adds an existing event to the current calendar"""
		self.events.add(event)
	
	
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
		slug  = orig = sluggify(self.name)
		count = 0
		while True:
			if not Calendar.objects.filter(slug=slug).count():
				break
			else:
				count += 1
				slug   = orig + '-' + str(count)
		self.slug = slug
	
	
	def __str__(self):
		return self.name
	
	
	def __unicode__(self):
		return unicode(self.name)
	
	
	def __repr__(self):
		"""docstring for __repr__"""
		return str(self.creator) + '/' + self.name
