from datetime import datetime

from dateutil import rrule
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from core.models import TimeCreatedModified


def first_login(self):
    delta = self.last_login - self.date_joined
    if delta.seconds == 0 and delta.days == 0:
        return True
    return False
setattr(User, 'first_login', property(first_login))


def get_all_users_future_events(user):
    """
    Retrieves all the future events for the given user
    """
    events = None
    try:
        events = EventInstance.objects.filter(event__calendar__in=list(user.calendars.all())).filter(end__gt=datetime.now())
    except Event.DoesNotExist:
        pass

    event_instances = []
    if events:
        for event in list(events.all()):
            event_instances.extend(event.future_instances())

    event_instances.sort(key=lambda instance: instance.start)
    return event_instances


class State:
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
    calendar = models.ForeignKey('Calendar', related_name='events', blank=True, null=True)
    creator = models.ForeignKey(User, related_name='created_events', null=True)
    created_from = models.ForeignKey('Event', related_name='duplicated_to', blank=True, null=True)
    state = models.SmallIntegerField(choices=State.choices, default=State.pending)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    contact_name = models.CharField(max_length=64, blank=True, null=True)
    contact_email = models.EmailField(max_length=128, blank=True, null=True)
    contact_phone = models.CharField(max_length=64, blank=True, null=True)

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

    event = models.ForeignKey(Event, related_name='event_instances')
    parent = models.ForeignKey(Event, related_name='children')
    location = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    interval = models.SmallIntegerField(default=Recurs.never, choices=Recurs.choices)
    until = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = 'events'
        ordering = ['start']

    def get_rrule(self):
        """
        Retrieve the base recurrence rule for the event. Using the
        end date so that it can retrieve an interval that is occurring
        now. Subtract your duration to get the start date.
        """
        if Event.Recurs.never == self.interval:
            return rrule.rrule(rrule.DAILY, dtstart=self.end, count=1)
        elif Event.Recurs.daily == self.interval:
            return rrule.rrule(rrule.DAILY, dtstart=self.end, until=self.until)
        elif Event.Recurs.weekly == self.interval:
            return rrule.rrule(rrule.WEEKLY, dtstart=self.end, until=self.until)
        elif Event.Recurs.biweekly == self.interval:
            return rrule.rrule(rrule.WEEKLY, interval=2, dtstart=self.end, until=self.until)
        elif Event.Recurs.monthly == self.interval:
            return rrule.rrule(rrule.MONTHLY, dtstart=self.end, until=self.until)

    def update_children(self):
        """
        Creates event instances based on the event.
        """
        self.children.all().delete()

        # rrule is based on end (to get events that occur now) so subtract duration to get start
        rule = self.get_rrule()
        duration = self.end - self.start
        for event_date in list(rule)[1:]:
            instance = EventInstance(event=self.event,
                                     parent=self,
                                     start=event_date - duration,
                                     end=event_date,
                                     location=self.location)
            instance.save()

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

    def delete(self, *args, **kwargs):
        self.children.all().delete()
        super(EventInstance, self).delete(*args, **kwargs)

    def __repr__(self):
        return '<' + str(self.start) + '>'


@receiver(post_save, sender=EventInstance)
def init_event_instances(sender, **kwargs):
    instance = kwargs['instance']
    try:
        #If we can find an object that matches this one, no update is needed
        EventInstance.objects.get(pk=instance.pk,
                                  start=instance.start,
                                  end=instance.end,
                                  location=instance.location,
                                  interval=instance.interval,
                                  until=instance.until)
        update = False
    except EventInstance.DoesNotExist:
        #Otherwise it's the first save or something has changed, update
        update = True
    

    if update:
        instance.update_children()