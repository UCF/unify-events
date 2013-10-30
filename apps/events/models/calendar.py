from datetime import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save

from core.models import TimeCreatedModified
from core.utils import pre_save_slug
import events.models
import settings


def get_main_calendar():
    """
    Retrieve the main calendar
    """
    return Calendar.objects.get(slug=settings.FRONT_PAGE_CALENDAR_SLUG)


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


def calendars_include_submitted(self):
    """
    Add and attribute to the User model to retrieve
    TODO: is this needed
    """
    return Calendar.objects.filter(
        models.Q(owner=self) |
        models.Q(editors=self) |
        models.Q(events__owner=self)).order_by('title').distinct()
setattr(User, 'calendars_include_submitted', property(calendars_include_submitted))


class Calendar(TimeCreatedModified):
    """
    Calendar
    """
    title = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, unique=True, blank=True)
    description = models.CharField(max_length=140, blank=True, null=True)
    owner = models.ForeignKey(User, related_name='owned_calendars', null=True)
    # TODO: possibly make Permission model (m2m on Calendar) user, permission
    editors = models.ManyToManyField(User, related_name='editor_calendars', null=True)
    admins = models.ManyToManyField(User, related_name='admin_calendars', null=True)
    subscriptions = models.ManyToManyField('Calendar', related_name='subscribed_calendars', null=True, symmetrical=False)

    class Meta:
        app_label = 'events'

    @property
    def is_main_calendar(self):
        is_main = False
        if self.slug == settings.FRONT_PAGE_CALENDAR_SLUG:
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
        during = Q(start__gte=start) & Q(start__lte=end) & Q(end__gte=start) & Q(end__lte=end)
        starts_before = Q(start__lte=start) & Q(end__gte=start) & Q(end__lte=end)
        ends_after = Q(start__gte=start) & Q(start__lte=end) & Q(end__gte=end)
        current = Q(start__lte=start) & Q(end__gte=end)
        _filter = during | starts_before | ends_after | current

        return self.event_instances.filter(_filter)

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
            'calendar': self.slug,
        })

    def import_event(self, event):
        """
        Given an event, will duplicate that event and import it into this
        calendar. Returns the newly created event.
        """
        copy = event.copy(calendar=self)
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
