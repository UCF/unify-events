from datetime import datetime

from dateutil import rrule
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from core.models import TimeCreatedModified
import events.models
import settings


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
    return events


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
    submit_to_main = models.BooleanField(default=False)

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

    @property
    def get_main_state(self):
        """
        Returns the State of an Event's copied Event on the Main Calendar.
        """
        status = None
        if self.submit_to_main == True:
            status = State.pending
            main_calendar = events.models.Calendar.objects.get(slug=settings.FRONT_PAGE_CALENDAR_SLUG)
            instances = main_calendar.event_instances.filter(event__created_from=self)
            if instances:
                status = instances[0].event.state
        return status

    def copy(self, *args, **kwargs):
        """
        Duplicates this Event creating another Event without a calendar set,
        and a link back to the original event created.

        This allows Events to be imported to other calendars and updates can be
        pushed back to the copied events.
        """
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
        copy.event_instances.add(*[i.copy(event=copy) for i in self.event_instances.filter(parent=None)])
        return copy
    
    def copy_to_main(self):
        """
        Creates a copy of the event for the main calendar
        """
        copy = self.copy()
        main_calendar = events.models.Calendar.objects.get(slug=settings.FRONT_PAGE_CALENDAR_SLUG)
        copy.calendar = main_calendar 
        copy.state = State.pending
        copy.save()

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
    parent = models.ForeignKey('EventInstance', related_name='children', null=True, blank=True)
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
        if EventInstance.Recurs.never == self.interval:
            return rrule.rrule(rrule.DAILY, dtstart=self.start, count=1)
        elif EventInstance.Recurs.daily == self.interval:
            return rrule.rrule(rrule.DAILY, dtstart=self.start, until=self.until)
        elif EventInstance.Recurs.weekly == self.interval:
            return rrule.rrule(rrule.WEEKLY, dtstart=self.start, until=self.until)
        elif EventInstance.Recurs.biweekly == self.interval:
            return rrule.rrule(rrule.WEEKLY, interval=2, dtstart=self.start, until=self.until)
        elif EventInstance.Recurs.monthly == self.interval:
            return rrule.rrule(rrule.MONTHLY, dtstart=self.start, until=self.until)

    def update_children(self):
        """
        Creates event instances based on the event.
        """
        self.children.all().delete()

        # Ensures children are deleted if a recurrence rule is removed
        if self.interval and self.until:
            # rrule is based on start date so add duration to get end date
            rule = self.get_rrule()
            duration = self.end - self.start
            for event_date in list(rule)[1:]:
                instance = EventInstance(event=self.event,
                                         parent=self,
                                         start=event_date,
                                         end=event_date + duration,
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
        
    def save(self, *args, **kwargs):
        """
        Update event instances only if a currently parent event instance
        does not already exist.
        """
        update = True
        try:
            # If we can find an object that matches this one, no update is needed
            EventInstance.objects.get(pk=self.pk,
                                      start=self.start,
                                      end=self.end,
                                      location=self.location,
                                      interval=self.interval,
                                      until=self.until,
                                      parent=None)
            update = False
        except ObjectDoesNotExist:
            # Something has changed
            pass
        
        super(EventInstance, self).save(*args, **kwargs)

        if update:
            self.update_children()
        
    def copy(self, *args, **kwargs):
        """
        Copies the event instance
        """
        copy = EventInstance(
            start=self.start,
            end=self.end,
            interval=self.interval,
            until=self.until,
            location=self.location,
            *args,
            **kwargs
        )
        copy.save()
        return copy

    def delete(self, *args, **kwargs):
        self.children.all().delete()
        super(EventInstance, self).delete(*args, **kwargs)

    def __repr__(self):
        return '<' + str(self.start) + '>'
    
    def __unicode__(self):
        return self.event.title


@receiver(pre_save, sender=EventInstance)
def update_event_instance_until(sender, instance, **kwargs):
    """
    Update the until time to match the starting of the event
    so the rrule will operate properly
    """
    if instance.until:
        instance.until = datetime.combine(instance.until.date(), instance.start.time())