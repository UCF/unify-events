from datetime import datetime
import copy

from dateutil import rrule
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_bleach.models import BleachField
from taggit.managers import TaggableManager

from core.models import TimeCreatedModified
from core.utils import pre_save_slug
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


def get_events_by_range(start, end, calendar=None, user=None):
    """
    Retrieves a range of events for the given calendar or user's calendars.
    """
    during = Q(start__gte=start) & Q(start__lte=end) & Q(end__gte=start) & Q(end__lte=end)
    starts_before = Q(start__lte=start) & Q(end__gte=start) & Q(end__lte=end)
    ends_after = Q(start__gte=start) & Q(start__lte=end) & Q(end__gte=end)
    current = Q(start__lte=start) & Q(end__gte=end)
    _filter = during | starts_before | ends_after | current

    if calendar:
        calendars = [calendar]
    elif user:
        calendars = list(user.calendars.all())
    else:
        raise AttributeError('Either a calendar or user must be supplied.')

    return EventInstance.objects.filter(_filter, event__calendar__in=calendars).order_by('start')


def map_event_range(start, end, events):
    """
    Processes a given set of EventInstances so that instances that fall within
    a range of dates are treated as a new instance per day within the start 
    and end date specified.
    Useful for listing all possible events that fall on a given set of days
    (i.e. week/month views.)

    NOTE: This function returns a list, NOT a queryset!
    """
    days = list(rrule.rrule(rrule.DAILY, dtstart=start, until=end))
    mapped_events = []

    for event in events:
        if event.start.date() is not event.end.date():
            duration = rrule.rrule(rrule.DAILY, dtstart=event.start.date(), until=event.end.date())
            for day in duration:
                event_by_day = copy.deepcopy(event)

                # Set the first day's end date/time to the start date/time, but at 23:59.
                if event.start.date() == day.date() and event.end.date() != day.date():
                    event_by_day.end = datetime.combine(day, datetime.max.time())
                # Set all-day event instance datetimes in a duration.
                # All day events should have 00:00 as start time and 23:59 as end time.
                if event.start.date() != day.date() and event.end.date() != day.date():
                    event_by_day.start = datetime.combine(day, datetime.min.time())
                    event_by_day.end = datetime.combine(day, datetime.max.time())
                # Set the last day's start time in a duration
                elif event.start.date() != day.date() and event.end.date() == day.date():
                    event_by_day.start = datetime.combine(day, datetime.min.time())
                    event_by_day.end = datetime.combine(day, datetime.time(event_by_day.end))

                if day in days:
                    mapped_events.append(event_by_day)
        else:
            if event.start in days:
                mapped_events.append(event)

    mapped_events.sort(key=lambda x: (x.start.date(), x.start.time(), x.end.time()))

    return mapped_events



class State:
    """
    This object provides the link between the time and places events are to
    take place and the purpose and name of the event as well as the calendar to
    which the events belong.
    """
    pending, posted, rereview = range(0, 3)
    choices = (
        (pending, 'pending'),
        (posted, 'posted'),
        (rereview, 'rereview')
    )

    @classmethod
    def get_id(cls, value):
        id_lookup = dict((v,k) for k,v in cls.choices)
        return id_lookup.get(value)

    @classmethod
    def get_string(cls, id):
        id_lookup = dict((k,v) for k,v in cls.choices)
        return id_lookup.get(id)


class Event(TimeCreatedModified):
    """
    Used to store a one time event or store the base information
    for a recurring event.
    """
    calendar = models.ForeignKey('Calendar', related_name='events', blank=True, null=True)
    creator = models.ForeignKey(User, related_name='created_events', null=True)
    created_from = models.ForeignKey('Event', related_name='duplicated_to', blank=True, null=True)
    state = models.SmallIntegerField(choices=State.choices, default=State.posted)
    canceled = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = BleachField(blank=True, null=True)
    contact_name = models.CharField(max_length=64)
    contact_email = models.EmailField(max_length=128)
    contact_phone = models.CharField(max_length=64, blank=True, null=True)
    category = models.ForeignKey('Category', related_name='events')
    tags = TaggableManager()

    class Meta:
        app_label = 'events'

    @property
    def is_re_review(self):
        re_review = False
        if self.state is State.rereview:
            re_review = True
        return re_review

    @property
    def has_instances(self):
        """
        Returns true if an event has more than one event instance
        (is "recurring" to the user.)
        """
        has_instances = False
        if self.event_instances.all().count() > 1:
            has_instances = True
        return has_instances

    @property
    def get_last_instance(self):
        """
        Retrieves the very last event instance out of all instances
        of this event.
        Makes up for Django's lack of support for negative indexing
        on querysets.
        """
        return list(self.event_instances.all())[-1]

    @property
    def get_all_parent_instances(self):
        """
        Returns all of this event's event instances that are the
        parents for those instances.
        """
        return EventInstance.objects.filter(event=self, parent=None)

    @property
    def is_submit_to_main(self):
        """
        Returns true if event has been submitted to the
        main calendar.
        """
        is_main = False
        if self.get_main_event():
            is_main = True

        return is_main

    @property
    def get_main_state(self):
        """
        Returns the State of an Event's copied Event on the Main Calendar.
        """
        main_status = None
        if self.calendar.pk != events.models.get_main_calendar().pk:
            main_event = self.get_main_event()
            if main_event:
                main_status = main_event.state
        return main_status

    def get_main_event(self):
        """
        Retrieves the event submitted to the main calendar
        """
        event = None

        # Compare against the original event
        original_event = self
        if self.created_from:
            original_event = self.created_from

        try:
            event = Event.objects.get(calendar__pk=settings.FRONT_PAGE_CALENDAR_PK, created_from=original_event)
        except Event.DoesNotExist:
            # The event has not been submitted to the main calendar
            pass
        return event

    def pull_updates(self, is_main_rereview=False):
        """
        Updates this Event with information from the event it was created
        from, if it exists.
        """
        updated_copy = None

        if self.created_from:
            # If main calendar copy then update everything except
            # the title and description and set for rereview
            if self.calendar.is_main_calendar and self.state is not State.pending:
                if is_main_rereview:
                    self.state = State.rereview
            else:
                self.title = self.created_from.title
                self.description = self.created_from.description

            self.canceled = self.created_from.canceled
            self.contact_email = self.created_from.contact_email
            self.contact_name = self.created_from.contact_name
            self.contact_phone = self.created_from.contact_phone
            self.category = self.created_from.category
            self.tags.set(*self.created_from.tags.all())
            self.event_instances.all().delete()
            self.modified=self.created_from.modified
            self.save()
            self.event_instances.add(*[i.copy(event=self) for i in self.created_from.event_instances.filter(parent=None)])
            updated_copy = self

        return updated_copy

    def copy(self, state=None, *args, **kwargs):
        """
        Duplicates this Event creating another Event without a calendar set
        (unless in *args/**kwargs), and a link back to the original event created.

        This allows Events to be imported to other calendars and updates can be
        pushed back to the copied events.
        """

        # Ensures that the originating event is always set as the created_from
        created_from = self
        if self.created_from:
            created_from = self.created_from

        # Allow state to be specified to copy as Pending (Main Calendar)
        if state is None:
            state = self.state

        copy = Event(creator=self.creator,
                     created_from=created_from,
                     canceled=self.canceled,
                     state=state,
                     title=self.title,
                     description=self.description,
                     category=self.category,
                     created=self.created,
                     modified=self.modified,
                     contact_name=self.contact_name,
                     contact_email=self.contact_email,
                     contact_phone=self.contact_phone,
                     *args,
                     **kwargs)
        copy.save()
        copy.tags.set(*self.tags.all())
        copy.event_instances.add(*[i.copy(event=copy) for i in self.event_instances.filter(parent=None)])
        return copy

    def delete(self, *args, **kwargs):
        """
        Delete all the event subscriptions.
        """
        for copy in self.duplicated_to.all():
            copy.delete()
        super(Event, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        """
        Generate permalink for this object
        """
        return reverse('event', kwargs={
            'slug': self.slug,
            'pk': self.pk,
        })

    def __str__(self):
        return self.title

    def __unicode__(self):
        return unicode(self.title)

    def __repr__(self):
        return '<' + str(self.calendar) + '/' + self.title + '>'

pre_save.connect(pre_save_slug, sender=Event)


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
    location = models.ForeignKey('Location', blank=True, null=True, related_name='event_instances');
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

    @property
    def get_rrule_name(self):
        """
        Retrieves the human-readable rrule defined by this
        EventInstance's interval value.
        """
        return self.Recurs.choices[self.interval][1]

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
                instance = EventInstance(event_id=self.event_id,
                                         parent=self,
                                         start=event_date,
                                         end=event_date + duration,
                                         location=self.location)
                instance.save()

    @property
    def title(self):
        return self.event.title

    @property
    def is_recurring(self):
        recurs = False
        if len(self.event.event_instances.all()) > 1:
            recurs = True
        return recurs

    @property
    def is_archived(self):
        if self.end < datetime.now():
            return True
        return False

    def get_absolute_url(self):
        """
        Generate permalink for this object
        """
        return reverse('event', kwargs={
            'pk': self.id,
            'slug': self.event.slug
        })

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
        return self.event.calendar.title + ' - ' + self.event.title


@receiver(pre_save, sender=EventInstance)
def update_event_instance_until(sender, instance, **kwargs):
    """
    Update the until time to match the starting of the event
    so the rrule will operate properly
    """
    if instance.until:
        instance.until = datetime.combine(instance.until.date(), instance.start.time())
