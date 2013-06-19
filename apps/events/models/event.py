from datetime import datetime

from dateutil import rrule
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from core.models import TimeCreatedModified
from events.models import Calendar


# TODO: move to ucfevent app
def first_login(self):
    delta = self.last_login - self.date_joined
    if delta.seconds == 0 and delta.days == 0:
        return True
    return False
setattr(User, 'first_login', property(first_login))


class Status:
    """
    This object provides the link between the time and places events are to
    take place and the purpose and name of the event as well as the calendar to
    which the events belong.
    """
    pending, posted, canceled = range(0, 3)
    choices = (
        (pending, 'pending'),
        (posted, 'posted'),
        (canceled, 'canceled')
    )


class Event(TimeCreatedModified):
    """
    Used to store a one time event or store the base information
    for a recurring event.
    """
    class Recurs:
        """
        Object which describes the time and place that an event is occurring
        """
        never, daily, weekly, biweekly, monthly, yearly = range(0, 6)
        choices = (
            (never, 'Never'),
            (daily, 'Daily'),
            (weekly, 'Weekly'),
            (biweekly, 'Biweekly'),
            (monthly, 'Monthly'),
            (yearly, 'Yearly'),
        )

    calendar = models.ForeignKey(Calendar, related_name='events', blank=True, null=True)
    creator = models.ForeignKey(User, related_name='created_events', null=True)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.pending)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    interval = models.SmallIntegerField(default=Recurs.never, choices=Recurs.choices)
    until = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = 'events'

    @property
    def slug(self):
        return slugify(self.title)

    @property
    def archived(self):
        if self.end < datetime.now():
            return True
        return False

    def get_rrule(self):
        if Event.Recurs.never == self.interval:
            return rrule.rrule(rrule.DAILY, dtstart=self.start, count=1)
        elif Event.Recurs.daily == self.interval:
            return rrule.rrule(rrule.DAILY, dtstart=self.start, until=self.until)
        elif Event.Recurs.weekly == self.interval:
            return rrule.rrule(rrule.WEEKLY, dtstart=self.start, until=self.until)
        elif Event.Recurs.biweekly == self.interval:
            return rrule.rrule(rrule.WEEKLY, interval=2, dtstart=self.start, until=self.until)
        elif Event.Recurs.monthly == self.interval:
            return rrule.rrule(rrule.MONTHLY, dtstart=self.start, until=self.until)

    def get_instances(self):
        """
        Retrieves/creates event instances based on the event.
        """
        rule = self.get_rrule()
        event_instances = []
        duration = self.end - self.start
        for event_date in list(rule):
            instance = EventInstance(event=self,
                                     creator=self.creator,
                                     status=self.status,
                                     title=self.title,
                                     description=self.description,
                                     start=event_date,
                                     end=event_date + duration,
                                     location=self.location)
            event_instances.append(instance)
        return event_instances

    def __str__(self):
        return self.title

    def __unicode__(self):
        return unicode(self.title)

    def __repr__(self):
        return '<' + str(self.calendar) + '/' + self.title + '>'


class EventInstance(TimeCreatedModified):
    """
    Used to store the actual event for recurring events. Can also be used when
    and event is different from the base recurring event.
    """
    event = models.ForeignKey(Event, related_name='instances')
    creator = models.ForeignKey(User, related_name='created_event_instances', null=True)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.pending)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    cancelled = models.BooleanField(default=False)

    class Meta:
        app_label = 'events'
        ordering = ['start']

    @property
    def archived(self):
        if self.end < datetime.now():
            return True
        return False

    def get_absolute_url(self):
        """
        Generate permalink for this object
        """
        from django.core.urlresolvers import reverse

        return reverse('event', kwargs={
            'calendar': self.event.calendar.slug,
            'instance_id': self.id,
        }) + self.event.slug + '/'

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

    def delete(self, *args, **kwargs):
        self.children.all().delete()
        super(EventInstance, self).delete(*args, **kwargs)

    def __repr__(self):
        return '<' + str(self.start) + '>'