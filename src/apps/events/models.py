from django.contrib.auth.models  import User
from django.db                   import models
from functions                   import sluggify
from fields                      import *
from datetime                    import datetime
from django.conf                 import settings as _settings

# Create your models here.
class Base(models.Model):
	created  = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	
	class Meta: abstract = True


class Profile(models.Model):
	user         = models.OneToOneField(User, related_name='profile')
	guid         = models.CharField(max_length = 100,null=True,unique=True)
	display_name = models.CharField(max_length = 100,null=True,blank=True)


def create_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
models.signals.post_save.connect(create_profile, sender=User)


def calendars(self):
	return Calendar.objects.filter(models.Q(owner=self)|models.Q(editors=self))
setattr(User,'calendars', property(calendars))


def calendars_include_submitted(self):
	return Calendar.objects.filter(
		models.Q(owner=self)|
		models.Q(editors=self)|
		models.Q(events__owner=self)).order_by('name').distinct()
setattr(User,'calendars_include_submitted', property(calendars_include_submitted))


def first_login(self):
	delta = self.last_login - self.date_joined
	if delta.seconds == 0 and delta.days == 0:
		return True
	return False
setattr(User,'first_login', property(first_login))


class Event(Base):
	"""This object provides the link between the time and places events are to
	take place and the purpose and name of the event as well as the calendard to
	which the events belong."""
	class Status:
		pending = 0
		posted  = 1
		choices = ((pending, 'pending'), (posted, 'posted'),)
	
	class Settings:
		default = {
			'receive_updates' : {
				'name'  : 'Receive Updates',
				'desc'  : 'Enable notification of updates to the event this was duplicated from.',
				'value' : False,
			},
		}
	
	#instances  = One to Many relationship with EventInstance
	calendar     = models.ForeignKey('Calendar', related_name='events', blank=True, null=True)
	created_from = models.ForeignKey('Event', related_name='duplicated_to', blank=True, null=True)
	state        = models.SmallIntegerField(choices=Status.choices, default=Status.pending)
	title        = models.CharField(max_length=128)
	description  = models.TextField(blank=True, null=True)
	settings     = SettingsField(default=Settings.default, null=True, blank=True)
	owner        = models.ForeignKey(User, related_name='owned_events', null=True)
	image        = models.FileField(upload_to=_settings.FILE_UPLOAD_PATH,null=True)
	tags         = models.ManyToManyField('Tag', related_name='events')
	additional   = models.TextField(blank=True, null=True)
	
	def pull_updates(self):
		"""Updates this Event with information from the event it was created 
		from, if it exists."""
		if self.created_from is None:
			return
		
		self.instances.all().delete()
		copy = self.created_from.copy(
			id=self.id,
			settings=self.settings,
			calendar=self.calendar
		)
		return copy
		
	
	
	def copy(self, *args, **kwargs):
		"""Duplicates this Event creating another Event without a calendar set, 
		and a link back to the original event created.
		
		This allows Events to be imported to other calendars and updates can be
		pushed back to the copied events."""
		copy = Event(
			created_from=self,
			state=self.state,
			title=self.title,
			description=self.description,
			created=self.created,
			modified=self.modified,
			*args,
			**kwargs
		)
		copy.save()
		copy.instances.add(*[i.copy(event=copy) for i in self.instances.filter(parent=None)])
		return copy
	
	@property
	def slug(self):
		return sluggify(self.title)

	@property
	def upcoming_instances(self):
		return self.instances.filter(start__gte = datetime.now())
	
	def on_owned_calendar(self,user):
		return self.calendar in user.calendars

	def __str__(self):
		return self.title
	
	def __unicode__(self):
		return unicode(self.title)
	
	def __repr__(self):
		return '<' + str(self.calendar) + '/' + self.title + '>'
	
	class Meta:
		ordering = ['instances__start']


class Tag(Base):
	name = models.CharField(max_length=64, unique=True)

	def __unicode__(self):
		return unicode(self.name)
	
	class Meta:
		ordering = ['name',]


class TagGroup(Base):
	name = models.CharField(max_length=128, unique=True)
	tags = models.ManyToManyField('Tag', related_name='tag_groups')
	
	def __str__(self):
		return str(self.name)
	
	def __unicode__(self):
		return unicode(self.name)


class EventInstance(Base):
	"""Object which describes the time and place that an event is occurring"""
	class Recurs:
		never, daily, weekly, biweekly, monthly, yearly = range(0,6)
		choices = (
			(never    , 'Never'),
			(daily    , 'Daily'),
			(weekly   , 'Weekly'),
			(biweekly , 'Biweekly'),
			(monthly  , 'Monthly'),
			(yearly   , 'Yearly'),
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
	interval  = models.SmallIntegerField(null=True, blank=True, default=Recurs.never, choices=Recurs.choices)
	limit     = models.PositiveSmallIntegerField(null=True, blank=True)
	parent    = models.ForeignKey('EventInstance', related_name='children', null=True, blank=True)
	
	def copy(self, *args, **kwargs):
		copy = EventInstance(
			start    = self.start,
			end      = self.end,
			interval = self.interval,
			limit    = self.limit,
			location = self.location.copy() if self.location else None,
			*args,
			**kwargs
		)
		copy.save()
		return copy
	
	
	@property
	def is_ongoing(self):
		return self.start <= datetime.now() <= self.end
	
	
	@property
	def title(self):
		return self.event.title
	
	
	@property
	def description(self):
		return self.event.description
	
	
	@property
	def tags(self):
		return self.event.tags
	
	
	def get_absolute_url(self):
		"""Generate permalink for this object"""
		from django.core.urlresolvers import reverse
		
		return reverse('event', kwargs={
			'calendar'    : self.event.calendar.slug,
			'instance_id' : self.id,
		}) + self.event.slug + '/'
		return r
	
	
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
		return '<' + str(self.start) + '>'

	class Meta:
		ordering = ['start']


class Location(Base):
	"""User inputted locations that specify where an event takes place"""
	#events     = One to Many relationship with EventInstance
	name        = models.CharField(max_length=128)
	description = models.TextField(blank=True, null=True)
	room        = models.CharField(max_length=64, blank=True, null=True)
	url         = models.URLField(blank=True, null=True, max_length=1024)
	
	def copy(self, *args, **kwargs):
		return Location.objects.create(
			name=self.name,
			description=self.description,
			coordinates=self.coordinates
		)
	
	
	def __str__(self):
		return str(self.name)
	
	
	def __unicode__(self):
		return unicode(self.__str__())
	
	
	def __repr__(self):
		return '<' + self.__str__() + '>'


class Calendar(Base):
	"""Calendar objects contain events that exist independent of the calendar,
	they may also subscribe to calendars which combine their owned events with
	events of other calendars."""
	#events       = One to Many relationship with Event
	#subscribers  = Many to Many with Calendar
	featured      = models.ManyToManyField('Event', related_name='featured_on')
	name          = models.CharField(max_length=64)
	slug          = models.CharField(max_length=64, unique=True, blank=True)
	owner         = models.ForeignKey(User, related_name='owned_calendars', null=True)
	editors       = models.ManyToManyField(User, related_name='edited_calendars')
	subscriptions = models.ManyToManyField('Calendar', symmetrical=False, related_name="subscribers")
	public        = models.BooleanField(default=False)
	shared        = models.BooleanField(default=False)

	@property
	def events_and_subs(self):
		"""Returns a queryset that combines this calendars event instances with
		its subscribed event instances"""
		from django.db.models import Q
		qs = EventInstance.objects.filter(
			Q(event__calendar=self) | 
			Q(Q(event__calendar__in=self.subscriptions.all()) & Q(event__state = Event.Status.posted))
		)
		return qs
	
	
	@property
	def event_instances(self):
		qs = EventInstance.objects.filter(event__calendar=self)
		return qs
	
	
	@property
	def featured_instances(self):
		from django.db.models import Q
		featured = [event.id for event in self.featured.all()]
		return EventInstance.objects.filter(
			Q(event__calendar=self) & Q(event__id__in=featured)
		)
	
	
	def get_absolute_url(self):
		"""Generate permalink for this object"""
		from django.core.urlresolvers import reverse
		
		return reverse('calendar', kwargs={
			'calendar' : self.slug,
		})
		return r
	
	
	def import_event(self, event):
		"""Given an event, will duplicate that event and import it into this 
		calendar. Returns the newly created event."""
		copy = event.copy(calendar=self)
		return copy
	
	
	def find_event_instances(self, start, end, qs=None):
		from django.db.models import Q
		during        = Q(start__gte=start) & Q(start__lte=end) & Q(end__gte=start) & Q(end__lte=end)
		starts_before = Q(start__gte=start) & Q(start__lte=end) & Q(end__gte=end)
		ends_after    = Q(start__lte=start) & Q(end__gte=start) & Q(end__lte=end)
		_filter       = during | starts_before | ends_after
		
		if qs is None:
			qs = self.events_and_subs.filter(_filter)
		else:
			qs = qs.filter(_filter)
		return qs
	
	
	def subscribe(self, *args):
		"""Subscribe to provided calendars"""
		self.subscriptions.add(*args)
	
	
	def unsubscribe(self, *args):
		"""Unsubscribe from provided calendars"""
		self.subscriptions.remove(*args)
	
	
	def is_creator(self, user):
		"""Determine if user is creator of this calendar"""
		return user == self.owner
	
	
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
		return '<' + str(self.owner) + '/' + self.name + '>'
