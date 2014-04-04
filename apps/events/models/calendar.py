from datetime import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save

from core.models import TimeCreatedModified
from core.utils import pre_save_slug
import events.models
from events.models.event import get_events_by_range
import settings


def get_main_calendar():
    """
    Retrieve the main calendar
    """
    return Calendar.objects.get(pk=settings.FRONT_PAGE_CALENDAR_PK)


def calendars(self):
    """
    Add and attribute to the User model to retrieve
    the calendars associated to them
    """
    return Calendar.objects.filter(Q(owner=self) | Q(admins=self) | Q(editors=self))
setattr(User, 'calendars', property(calendars))


def editable_calendars(self):
    """
    Returns the list of calendars the user can edit
    """
    return Calendar.objects.filter(Q(owner=self) | Q(admins=self))
setattr(User, 'editable_calendars', property(editable_calendars))


class Calendar(TimeCreatedModified):
    """
    Calendar
    """
    title = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, blank=True)
    description = models.CharField(max_length=140, blank=True, null=True)
    owner = models.ForeignKey(User, related_name='owned_calendars', null=True)
    editors = models.ManyToManyField(User, related_name='editor_calendars', null=True)
    admins = models.ManyToManyField(User, related_name='admin_calendars', null=True)
    subscriptions = models.ManyToManyField('Calendar', related_name='subscribed_calendars', null=True, symmetrical=False)

    class Meta:
        app_label = 'events'

    @property
    def is_main_calendar(self):
        is_main = False
        if self.pk == settings.FRONT_PAGE_CALENDAR_PK:
            is_main = True

        return is_main

    @property
    def subscribing_calendars(self):
        """
        Returns all calendars that are currently subscribed to this calendar
        """
        return Calendar.objects.filter(subscriptions=self.id)

    @property
    def event_instances(self):
        """
        Get all the event instances for this calendar
        """
        return events.models.EventInstance.objects.filter(event__calendar=self)

    def copy_future_events(self, calendar):
        """
        Copy all future events to a new calendar.
        """
        events = self.events.filter(event_instances__end__gte=datetime.now(), created_from=None).distinct()
        for event in events:
            calendar.import_event(event)

    def delete_subscribed_events(self, calendar):
        """
        Deletes all the subscribed events related to the calendar
        """
        events = self.events.filter(created_from__calendar=calendar)
        for event in events:
            event.delete()

    def future_event_instances(self):
        """
        Get all future event instances for this calendar, including
        subscribed event instances
        """
        return self.event_instances.filter(end__gte=datetime.now())

    def range_event_instances(self, start, end):
        """
        Retrieve all the instances that are within the start and end date,
        including subscribed event instances
        """
        return get_events_by_range(start, end, self)

    @property
    def archived_event_instances(self):
        """
        Returns a queryset of this calendar's archived event instances
        """
        qs = events.models.EventInstance.objects.filter(
            Q(Q(event__calendar=self) & Q(is_archived=True))
        )
        return qs

    def get_absolute_url(self):
        """
        Generate permalink for this object
        """
        return reverse('calendar', kwargs={
            'pk': self.pk,
            'slug': self.slug,
        })

    def import_event(self, event):
        """
        Given an event, will duplicate that event and import it into this
        calendar. Returns the newly created event.
        """
        # Make state pending if copying for Main Calendar
        state = None
        if self.is_main_calendar:
            state = events.models.State.pending
        copy = event.copy(calendar=self, state=state)
        return copy

    def is_creator(self, user):
        """
        Determine if user is creator of this calendar
        """
        return user == self.owner

    def __str__(self):
        return self.title

    def __unicode__(self):
        return unicode(self.title)

    def __repr__(self):
        """docstring for __repr__"""
        return '<' + str(self.owner) + '/' + self.title + '>'

pre_save.connect(pre_save_slug, sender=Calendar)
