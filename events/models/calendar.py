from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save

from core.models import TimeCreatedModified
from core.utils import pre_save_slug
import events.models
from events.models.event import get_events_by_range
from events.utils import generic_ban_urls
import settings


def get_main_calendar():
    """
    Retrieve the main calendar
    """
    return Calendar.objects.get(pk=settings.FRONT_PAGE_CALENDAR_PK)


def calendars(self):
    """
    Add an attribute to the User model to retrieve
    the calendars associated to them.

    NOTE:
    This query generates an outer join for admins (m) and an outer join
    for editors (n), which can result in a m*n result set, without the
    distinct().
    """
    return Calendar.objects.filter(Q(owner=self) | Q(admins=self) | Q(editors=self)).distinct()
setattr(User, 'calendars', property(calendars))


def active_calendars(self):
    """
    Add an attribute to the User model to retrieve
    the calendars associated to them.

    NOTE:
    This query generates an outer join for admins (m) and an outer join
    for editors (n), which can result in a m*n result set, without the
    distinct().
    """
    return Calendar.objects.filter(Q(owner=self) | Q(admins=self) | Q(editors=self)).filter(active=True).distinct()
setattr(User, 'active_calendars', property(active_calendars))


def editable_calendars(self):
    """
    Returns the list of calendars the user can edit
    """
    return Calendar.objects.filter(Q(owner=self) | Q(admins=self)).distinct()
setattr(User, 'editable_calendars', property(editable_calendars))


def active_editable_calendars(self):
    """
    Returns the list of calendars the user can edit
    """
    return Calendar.objects.filter(Q(owner=self) | Q(admins=self)).filter(active=True).distinct()
setattr(User, 'active_editable_calendars', property(active_editable_calendars))

class CalendarManager(models.Manager):
    def active_calendars(self):
        return self.filter(active=True)

    def inactive_calendars(self):
        return self.filter(active=False)

    def with_recent_events(self):
        expiration = datetime.now() - timedelta(days=settings.CALENDAR_EXPIRATION_DAYS)
        return self.filter(events__event_instances__start__gte=expiration).distinct()

    def without_recent_events(self):
        active = self.with_recent_events()
        return Calendar.objects.exclude(pk__in=active)

    def invalid_named_calendars(self):
        return Calendar.objects.filter(title__in=settings.DISALLOWED_CALENDAR_TITLES).exclude(pk=settings.FRONT_PAGE_CALENDAR_PK)

class Calendar(TimeCreatedModified):
    """
    Calendar
    """
    title = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, blank=True)
    description = models.CharField(max_length=140, blank=True, null=True)
    owner = models.ForeignKey(User, related_name='owned_calendars', null=True, on_delete=models.CASCADE)
    editors = models.ManyToManyField(User, related_name='editor_calendars', blank=True)
    admins = models.ManyToManyField(User, related_name='admin_calendars', blank=True)
    subscriptions = models.ManyToManyField('Calendar', related_name='subscribed_calendars', blank=True, symmetrical=False)
    active = models.BooleanField(blank=False, null=False, default=True)
    trusted = models.BooleanField(blank=False, null=False, default=False)
    objects = CalendarManager()

    class Meta:
        app_label = 'events'
        ordering = ['title']

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
        future_events = self.events.filter(event_instances__end__gte=datetime.now(), created_from=None, state=events.models.State.posted).distinct()
        for event in future_events:
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
        canonical_root = settings.CANONICAL_ROOT
        relative_path = reverse('events.views.event_views.calendar', kwargs={
                            'pk': self.pk,
                            'slug': self.slug,
                        })
        return canonical_root + relative_path

    def get_json_details(self):
        """
        Generate a permalink to the single object details for this object
        """
        canonical_root = settings.CANONICAL_ROOT
        relative_path = reverse('events.views.event_views.calendar', kwargs={
            'pk': self.pk,
            'slug': self.slug,
            'format': 'json'
        })
        return canonical_root + relative_path

    def import_event(self, event):
        """
        Given an event, will duplicate that event and import it into this
        calendar. Returns the newly created event.
        """
        # Make state pending if copying for Main Calendar
        state = None
        if self.is_main_calendar:
            if event.calendar.trusted:
                state = events.models.State.posted
            else:
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
        return str(self.title)

    def __repr__(self):
        """docstring for __repr__"""
        return '<' + str(self.owner) + '/' + self.title + '>'

pre_save.connect(pre_save_slug, sender=Calendar)
post_save.connect(generic_ban_urls, sender=Calendar)
# using pre_delete because all the objects may not exist if done via
# post_delete (ex. event.calendar or event.tags if deleting a calendar)
# No harm done if the delete doesn't go through. Just causes a single
# miss on varnish.
pre_delete.connect(generic_ban_urls, sender=Calendar)

