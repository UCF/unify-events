from core.models import TimeCreatedModified

from datetime import datetime

from dateutil import rrule

from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


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
        (canceled, 'canceled'),
    )


class Event(TimeCreatedModified):
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

    calendar = models.ForeignKey('Calendar', related_name='events', blank=True, null=True)
    creator = models.ForeignKey(User, related_name='created_events', null=True)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.pending)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    interval = models.SmallIntegerField(null=True, blank=True, default=Recurs.never, choices=Recurs.choices)
    until = models.DateTimeField(null=True, blank=True)
    # TODO: event instances

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
    def upcoming_instances(self):
        return self.instances.filter(start__gte=datetime.now())

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

    def __str__(self):
        return self.title

    def __unicode__(self):
        return unicode(self.title)

    def __repr__(self):
        return '<' + str(self.calendar) + '/' + self.title + '>'

    class Meta:
        ordering = ['instances__start']


class EventInstance(TimeCreatedModified):
    @classmethod
    def next_monthly_date(cls, d):
        """
        Next date in recurring by month series from datetime d
        """
        m = d.date().month
        if m != 12:
            m += 1
        else:
            m = 1
        return d.replace(month=m)

    @classmethod
    def next_yearly_date(cls, d):
        """
        Next date in recurring by year series from datetime d
        """
        from datetime import datetime
        y = d.date().year
        return d.replace(year=y+1)

    @classmethod
    def next_arbitrary_date(cls, d, delta):
        """
        Next date in recurring by delta days from datetime d
        """
        from datetime import timedelta
        delta = timedelta(days=delta)
        return d + delta

    @classmethod
    def next_date(cls, d, i):
        """
        Given a datetime d, and Recurring interval i (Recurring.daily,
        Recurring.weekly, etc), will return the next date in the series
        """
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
    creator = models.ForeignKey(User, related_name='created_events', null=True)
    state = models.SmallIntegerField(choices=Status.choices, default=Status.pending)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        app_label = 'events'

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

    class Meta:
        ordering = ['start']