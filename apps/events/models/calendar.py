from datetime import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from core.models import TimeCreatedModified
import events.models
import settings


def get_main_calendar(self):
    """
    Retrieve the main calendar
    """
    return Calendar.objects.get(slug=settings.FRONT_PAGE_CALENDAR_SLUG)


def calendars(self):
    """
    Add and attribute to the User model to retrieve
    the calendars associated to them
    """
    return Calendar.objects.filter(Q(owner=self) | Q(editors=self))
setattr(User, 'calendars', property(calendars))


def calendars_include_submitted(self):
    """
    Add and attribute to the User model to retrieve
    TODO: is this needed
    """
    return Calendar.objects.filter(
        models.Q(owner=self) |
        models.Q(editors=self) |
        models.Q(events__owner=self)).order_by('name').distinct()
setattr(User, 'calendars_include_submitted', property(calendars_include_submitted))


class Calendar(TimeCreatedModified):
    """
    Calendar
    """
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64, unique=True, blank=True)
    description = models.CharField(max_length=140, blank=True, null=True)
    owner = models.ForeignKey(User, related_name='owned_calendars', null=True)
    editors = models.ManyToManyField(User, related_name='editor_calendars', null=True)

    class Meta:
        app_label = 'events'
    
    @property
    def events_and_subs(self):
        """
        Returns a queryset that combines this calendars event instances with
        its subscribed event instances
        """
        from django.db.models import Q
        qs = events.models.EventInstance.objects.filter(
            Q(event__calendar=self) |
            Q(Q(event__calendar__in=self.subscriptions.all()) & Q(event__state=events.models.State.posted))
        )
        return qs

    @property
    def event_instances(self):
        """
        Get all the event instances for this calendar
        """
        return events.models.EventInstance.objects.filter(event__calendar=self)
    
    def future_event_instances(self):
        """
        Get all future event instances for this calendar
        """
        return self.event_instances.filter(end__gte=datetime.now())

    def range_event_instances(self, start, end):
        """
        Retrieve all the instances that are within the start and end date
        """
        from django.db.models import Q
        during = Q(start__gte=start) & Q(start__lte=end) & Q(end__gte=start) & Q(end__lte=end)
        starts_before = Q(start__lte=start) & Q(end__gte=start) & Q(end__lte=end)
        ends_after = Q(start__gte=start) & Q(start__lte=end) & Q(end__gte=end)
        current = Q(start__lte=start) & Q(end__gte=end)
        _filter = during | starts_before | ends_after | current

        return self.event_instances.filter(_filter)

    @property
    def archived_event_instances(self):
        pass

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

    def generate_slug(self):
        """
        Generates a slug from the calendar's name, ensuring that the slug
        is not already used by another calendar.
        """
        slug = orig = slugify(self.name)
        count = 0
        while True:
            if not Calendar.objects.filter(slug=slug).count():
                break
            else:
                count += 1
                slug = orig + '-' + str(count)
        self.slug = slug

    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)

    def __repr__(self):
        """docstring for __repr__"""
        return '<' + str(self.owner) + '/' + self.name + '>'
    

@receiver(pre_save, sender=Calendar)
def save(sender, **kwargs):
    """
    Generate a slug before the calendar is saved
    """
    instance = kwargs['instance']
    instance.generate_slug()