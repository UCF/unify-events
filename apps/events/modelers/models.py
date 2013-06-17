from core.models import TimeCreatedModified

from datetime import datetime

from django.conf import settings as _settings
from django.contrib.auth.models import User
from django.db import models

from fields import *


def full_name(self):
    return self.first_name + ' ' + self.last_name
setattr(User, 'full_name', property(full_name))


def first_login(self):
    delta = self.last_login - self.date_joined
    if delta.seconds == 0 and delta.days == 0:
        return True
    return False
setattr(User, 'first_login', property(first_login))


class Event(TimeCreatedModified):
    """This object provides the link between the time and places events are to
    take place and the purpose and name of the event as well as the calendard to
    which the events belong."""
    class Status:
        pending = 0
        posted = 1
        canceled = 2
        choices = (
            (pending, 'pending'),
            (posted, 'posted'),
            (canceled, 'canceled'),
        )

    class Settings:
        default = {
            'receive_updates' : {
                'name': 'Receive Updates',
                'desc': 'Enable notification of updates to the event this was duplicated from.',
                'value': False,
            },
        }

    class Contact:
        internal, directory, freeform = range(0, 3)
        choices = (
            (internal, 'internal'),
            (directory, 'directory'),
            (freeform, 'freeform'),
        )

    #instances    = One to Many relationship with EventInstance
    calendar = models.ForeignKey('Calendar', related_name='events', blank=True, null=True)
    created_from = models.ForeignKey('Event', related_name='duplicated_to', blank=True, null=True)
    state = models.SmallIntegerField(choices=Status.choices, default=Status.pending)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    settings = SettingsField(default=Settings.default, null=True, blank=True)
    owner = models.ForeignKey(User, related_name='owned_events', null=True)
    image = models.FileField(upload_to=_settings.FILE_UPLOAD_PATH, null=True)
    tags = models.ManyToManyField('Tag', related_name='events')
    contact_use = models.SmallIntegerField(choices=Contact.choices, default=Contact.directory)
    # TODO
    #contact_freeform
    #contact_directory
    contact_name = models.CharField(max_length=64, blank=True, null=True)
    contact_email = models.EmailField(max_length=128, blank=True, null=True)
    contact_phone = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        app_label = 'events'

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

    @property
    def has_contact(self):
        return bool(self.contact_phone or self.contact_email)

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


class Tag(TimeCreatedModified):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        app_label = 'events'

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Tag, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        ordering = ['name', ]


class EventInstance(TimeCreatedModified):
    """Object which describes the time and place that an event is occurring"""
    class Recurs:
        never, daily, weekly, biweekly, monthly, yearly = range(0,6)
        choices = (
            (never, 'Never'),
            (daily, 'Daily'),
            (weekly, 'Weekly'),
            (biweekly, 'Biweekly'),
            (monthly, 'Monthly'),
            (yearly, 'Yearly'),
        )


        @classmethod
        def next_monthly_date(cls, d):
            """Next date in recurring by month series from datetime d"""
            from datetime import datetime
            m = d.date().month
            if m != 12:
                m += 1
            else:
                m = 1
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
                cls.daily: lambda: cls.next_arbitrary_date(d, 1),
                cls.weekly: lambda: cls.next_arbitrary_date(d, 7),
                cls.biweekly: lambda: cls.next_arbitrary_date(d, 14),
                cls.monthly: lambda: cls.next_monthly_date(d),
                cls.yearly: lambda: cls.next_yearly_date(d),
            }.get(i, lambda: None)()

            if next is None:
                raise ValueError('Invalid constant provided for interval type')

            return next

    event = models.ForeignKey('Event', related_name='instances')
    location = models.ForeignKey('Location', related_name='events', null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    interval = models.SmallIntegerField(null=True, blank=True, default=Recurs.never, choices=Recurs.choices)
    until = models.DateTimeField(null=True, blank=True)
    parent = models.ForeignKey('EventInstance', related_name='children', null=True, blank=True)

    class Meta:
        app_label = 'events'

    def copy(self, *args, **kwargs):
        copy = EventInstance(
            start=self.start,
            end=self.end,
            interval=self.interval,
            until=self.until,
            location=self.location.copy() if self.location else None,
            *args,
            **kwargs
        )
        copy.save()
        return copy

    @property
    def is_ongoing(self):
        return self.start <= datetime.now() <= self.end

    @property
    def owner(self):
        return self.event.owner

    @property
    def title(self):
        return self.event.title

    @property
    def description(self):
        return self.event.description

    @property
    def tags(self):
        return self.event.tags

    @property
    def has_contact(self):
        return self.event.has_contact

    @property
    def contact(self):
        return {
            'name'  : self.event.contact_name,
            'phone' : self.event.contact_phone,
            'email' : self.event.contact_email,
        }

    @property
    def sibling_upcoming(self):
        return self.event.upcoming_instances.exclude(pk=self.pk)

    def get_absolute_url(self):
        """Generate permalink for this object"""
        from django.core.urlresolvers import reverse

        return reverse('event', kwargs={
            'calendar': self.event.calendar.slug,
            'instance_id': self.id,
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
                until=self.until
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
        if self.until is None or self.interval is None: return

        instance = self
        start = instance.start

        while start <= self.until:
            delta = instance.end - instance.start
            start = EventInstance.Recurs.next_date(instance.start, self.interval)
            end = start + delta
            instance = self.children.create(
                event=instance.event,
                start=start,
                end=end,
                location=self.location
            )

    def delete(self, *args, **kwargs):
        self.children.all().delete()
        super(EventInstance, self).delete(*args, **kwargs)

    def __repr__(self):
        return '<' + str(self.start) + '>'

    class Meta:
        ordering = ['start']


class Location(TimeCreatedModified):
    """User inputted locations that specify where an event takes place"""
    #events     = One to Many relationship with EventInstance
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    room = models.CharField(max_length=64, blank=True, null=True)
    url = models.URLField(blank=True, null=True, max_length=1024)

    class Meta:
        app_label = 'events'

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