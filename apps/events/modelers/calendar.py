from core.models import TimeCreatedModified

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify


def calendars(self):
    """
    Add and attribute to the User model to retrieve
    the calendars associated to them
    """
    return Calendar.objects.filter(owner=self)
setattr(User, 'calendars', property(calendars))


def calendars_include_submitted(self):
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
    owner = models.ForeignKey(User, related_name='owned_calendars', null=True)

    class Meta:
        app_label = 'events'

    @property
    def events(self):
        return self.events

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

    def find_event_instances(self, start, end, qs=None):
        """
        Given a range of datetimes defined by start and end, will return a
        queryset which should return all events for the current calendar in the
        range provided.  An optional queryset argument can be passed to append
        the resulting filtered queryset to.
        """
        from django.db.models import Q
        during = Q(start__gte=start) & Q(start__lte=end) & Q(end__gte=start) & Q(end__lte=end)
        starts_before = Q(start__gte=start) & Q(start__lte=end) & Q(end__gte=end)
        ends_after = Q(start__lte=start) & Q(end__gte=start) & Q(end__lte=end)
        _filter = during | starts_before | ends_after

        if qs is None:
            qs = self.events_and_subs.filter(_filter)
        else:
            qs = qs.filter(_filter)
        return qs

    def is_creator(self, user):
        """
        Determine if user is creator of this calendar
        """
        return user == self.owner

    def save(self, *args, **kwargs):
        print(self.slug)
        self.generate_slug()
        super(Calendar, self).save(*args, **kwargs)

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