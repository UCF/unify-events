from datetime import datetime
import copy

from dateutil import rrule
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_bleach.models import BleachField
from taggit.managers import TaggableManager
from taggit.models import Tag

from PIL import Image

from core.models import TimeCreatedModified
from core.utils import pre_save_slug
from events.utils import event_ban_urls
from events.utils import generic_ban_urls
import events.models


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
        events = EventInstance.objects.filter(event__calendar__in=list(user.active_calendars.all())).filter(end__gt=datetime.now())
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
        calendars = list(user.active_calendars.all())
    else:
        raise AttributeError('Either a calendar or user must be supplied.')

    return EventInstance.objects.filter(_filter, event__calendar__in=calendars)


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
                    # Try to catch weird instances where the endtime is not set (from imported events)
                    if not event.end.time():
                        event_by_day.end = datetime.combine(day, datetime.max.time())
                    else:
                        event_by_day.end = datetime.combine(day, datetime.time(event_by_day.end))

                if day in days:
                    mapped_events.append(event_by_day)
        else:
            if event.start in days:
                mapped_events.append(event)

    # Sorting by end date ensures all day events are on top.
    # added to support python version < 2.7, otherwise timedelta has total_seconds()
    mapped_events.sort(key=lambda x: (x.start.date(), x.start.time(), -((x.end - datetime.now()).microseconds + ((x.end - datetime.now()).seconds + (x.end - datetime.now()).days*24*3600) * 1e6) /1e6))

    return mapped_events

def featured_image_upload_location(instance, filename):
    """
    Provides a unique location for uploading header
    images, in order to keep the file system organized.
    """
    return f"featured/{instance.event.pk}/{filename}"

def validate_feature_event_desktop_dimensions(image):
    """
    Provides validation of the desktop header
    size and can be assigned to the model field.
    """
    img = Image.open(image)
    max_width = 1140
    max_height = 350

    if img.width > max_width or img.height > max_height:
        raise ValidationError(
            f"The desktop header image cannot exceed {max_width}x{max_height}"
        )

def validate_feature_event_mobile_dimensions(image):
    """
    Provides a unique location for uploading header
    images, in order to keep the file system organized.
    """
    img = Image.open(image)
    max_width = 575
    max_height = 575

    if img.width > max_width or img.height > max_height:
        raise ValidationError(
            f"The mobile header image cannot exceed {max_width}x{max_height}"
        )


class PromotedTag(models.Model):
    tag = models.OneToOneField(Tag, on_delete=models.CASCADE, related_name='promoted')

    class Meta:
        app_label = 'events'

    def __str__(self):
        return self.tag.name

    def __unicode__(self):
        return self.tag.name

# Special function for determining if a Tag is promoted
def tag_is_promoted(self):
    return hasattr(self, 'promoted')

setattr(Tag, 'is_promoted', property(tag_is_promoted))

class State:
    """
    This object provides the link between the time and places events are to
    take place and the purpose and name of the event as well as the calendar to
    which the events belong.
    """
    pending, posted, rereview = list(range(0, 3))
    # All available choices
    choices = (
        (pending, 'pending'),
        (posted, 'posted'),
        (rereview, 'rereview')
    )
    # Choices only available to regular users (non-Superusers)
    user_choices = (
        (pending, 'pending'),
        (posted, 'posted')
    )

    @classmethod
    def get_id(cls, value):
        id_lookup = dict((v,k) for k,v in cls.choices)
        return id_lookup.get(value)

    @classmethod
    def get_string(cls, id):
        id_lookup = dict((k,v) for k,v in cls.choices)
        return id_lookup.get(id)

    # Return states that represent an event that is available publicly
    @classmethod
    def get_published_states(self):
        return [self.get_id('posted'), self.get_id('rereview')]


class Event(TimeCreatedModified):
    """
    Used to store a one time event or store the base information
    for a recurring event.
    """
    calendar = models.ForeignKey('Calendar', related_name='events', blank=True, null=True, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, related_name='created_events', null=True, on_delete=models.CASCADE)
    created_from = models.ForeignKey('Event', related_name='duplicated_to', blank=True, null=True, on_delete=models.CASCADE)
    state = models.SmallIntegerField(choices=State.user_choices, default=State.posted)
    canceled = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = BleachField()
    contact_name = models.CharField(max_length=64)
    contact_email = models.EmailField(max_length=128, blank=False, null=True)
    contact_phone = models.CharField(max_length=64, blank=True, null=True)
    category = models.ForeignKey('Category', related_name='events', on_delete=models.CASCADE)
    tags = TaggableManager()
    registration_link = models.URLField(max_length=400, blank=True, null=True)
    registration_info = models.TextField(max_length=255, blank=True, null=True)

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
    def has_future_instances(self):
        """
        Returns true if an event has more than one even instance
        in the future
        """
        today = timezone.now().date()
        has_instances = False
        if self.event_instances.filter(start__gte=today).count() > 1:
            has_instances = True
        return has_instances

    @property
    def get_first_instance(self):
        """
        Returns the very first event instance out of all instances
        of this event.
        """
        return self.event_instances.all()[0]

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
    def get_title_canceled(self):
        """
        Returns an event title prefixed with "CANCELED" if the event
        has been canceled.
        """
        title = self.title
        if self.canceled:
            title = 'CANCELED: ' + title
        return title


    def get_copied_event(self):
        """
        Finds the first instance of this event on the next tier
        of calendars.
        """
        event = None

        if self.calendar is None:
            return None

        # Compare against the original event
        original_event = self
        if self.created_from:
            original_event = self.created_from

        try:
            event = Event.objects.filter(calendar__tier__lt=self.calendar.tier, created_from=original_event).first()
        except Event.DoesNotExist:
            pass

        return event


    @property
    def get_copied_state(self):
        """
        Get's the state of the copied version of the event
        """
        copied_status = None
        copied_event = self.get_copied_event()
        if copied_event:
            copied_status = copied_event.state
        return copied_status


    @property
    def is_submit_to_calendar(self):
        """
        Returns true if event has been submitted
        to another calendar.
        """
        is_copied = False
        if self.get_copied_event():
            is_copied = True

        return is_copied


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

    def pull_updates(self, is_rereview=False):
        """
        Updates this Event with information from the event it was created
        from, if it exists.
        """
        updated_copy = None

        if self.created_from:
            # If main calendar copy then update everything except
            # the title and description and set for rereview
            if self.state is not State.pending and is_rereview:
                self.state = State.rereview
            else:
                self.title = self.created_from.title
                self.description = self.created_from.description

            self.canceled = self.created_from.canceled
            self.contact_email = self.created_from.contact_email
            self.contact_name = self.created_from.contact_name
            self.contact_phone = self.created_from.contact_phone
            self.category = self.created_from.category
            self.registration_link = self.created_from.registration_link
            self.registration_info = self.created_from.registration_info
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
                     registration_link=self.registration_link,
                     registration_info=self.registration_info,
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
        # Get the first event instance's pk
        instance = self.get_first_instance
        canonical_root = settings.CANONICAL_ROOT
        relative_path = reverse('events.views.event_views.event', kwargs={'pk': instance.pk, 'slug': self.slug})
        return canonical_root + relative_path

    def get_json_details(self):
        """
        Generate a permalink to the single object details for this object
        """
        # Get the first event instance's pk
        instance = self.get_first_instance
        canonical_root = settings.CANONICAL_ROOT
        relative_path = reverse('events.views.event_views.event', kwargs={
            'pk': instance.pk,
            'slug': self.slug,
            'format': 'json'
        })
        return canonical_root + relative_path

    def __str__(self):
        return self.title

    def __unicode__(self):
        return str(self.title)

    def __repr__(self):
        return '<' + str(self.calendar) + '/' + self.title + '>'

pre_save.connect(pre_save_slug, sender=Event)
post_save.connect(event_ban_urls, sender=Event)
# using pre_delete because all the objects may not exist if done via
# post_delete (ex. event.calendar or event.tags if deleting a calendar)
# No harm done if the delete doesn't go through. Just causes a single
# miss on varnish.
pre_delete.connect(event_ban_urls, sender=Event)

post_save.connect(generic_ban_urls, sender=Tag)
# using pre_delete because all the objects may not exist if done via
# post_delete (ex. event.calendar or event.tags if deleting a calendar)
# No harm done if the delete doesn't go through. Just causes a single
# miss on varnish.
pre_delete.connect(generic_ban_urls, sender=Tag)


class EventInstance(TimeCreatedModified):
    """
    Used to store the actual event for recurring events. Can also be used when
    and event is different from the base recurring event.
    """
    class Recurs:
        """
        Object which describes the time and place that an event is occurring
        """
        never, daily, weekly, biweekly, monthly, yearly = list(range(0, 6))
        choices = (
            (never, 'Never'),
            (daily, 'Daily'),
            (weekly, 'Weekly'),
            (biweekly, 'Biweekly'),
            (monthly, 'Monthly'),
            (yearly, 'Yearly'),
        )

    unl_eventdatetime_id = models.PositiveIntegerField(blank=True, null=True) # Necessary to map redirects to events from UNL Events system
    event = models.ForeignKey(Event, related_name='event_instances', on_delete=models.CASCADE)
    parent = models.ForeignKey('EventInstance', related_name='children', null=True, blank=True, on_delete=models.CASCADE)
    location = models.ForeignKey('Location', blank=True, null=True, related_name='event_instances', on_delete=models.CASCADE)
    virtual_url = models.CharField(max_length=1000, blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    interval = models.SmallIntegerField(default=Recurs.never, choices=Recurs.choices)
    until = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = 'events'
        # Sorting by end date ensures all day events are on top
        ordering = ['start', '-end', 'id']

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
                                         location=self.location,
                                         virtual_url=self.virtual_url)
                instance.save()

    @property
    def title(self):
        return self.event.title

    @property
    def slug(self):
        return self.event.slug

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
        canonical_root = settings.CANONICAL_ROOT
        relative_path = reverse('events.views.event_views.event', kwargs={'pk': self.pk, 'slug': self.slug})
        return canonical_root + relative_path

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
                                      virtual_url=self.virtual_url,
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
            virtual_url=self.virtual_url,
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

class FeaturedEventManager(models.Manager):
    """
    Manager for retrieving featured events
    """
    def get_active(self):
        today = timezone.now().date()
        result = self.filter(
            start_date__lte=today,
            event__event_instances__start__gte=today
        ).order_by(
            '-start_date'
        ).first()

        return result


class FeaturedEvent(models.Model):
    """
    An event that can be featured on the home page.
    """
    event = models.ForeignKey('Event', related_name='featured', null=False, blank=False, on_delete=models.CASCADE)
    desktop_feature_image = models.ImageField(
        validators=[validate_feature_event_desktop_dimensions],
        upload_to=featured_image_upload_location
    )
    mobile_feature_image = models.ImageField(
        validators=[validate_feature_event_mobile_dimensions],
        upload_to=featured_image_upload_location
    )
    start_date = models.DateField()
    objects = FeaturedEventManager()

    @property
    def active(self):
        if self.event.has_future_instances:
            return True

        return False

    def __unicode__(self):
        """
        The unicode representation of the object
        """
        return f"{self.event.title} (Featured)"

    def __str__(self):
        """
        The string representation of the object
        """
        return f"{self.event.title} (Featured)"


@receiver(pre_save, sender=EventInstance)
def update_event_instance_until(sender, instance, **kwargs):
    """
    Update the until time to match the starting of the event
    so the rrule will operate properly
    """
    if instance.until:
        instance.until = datetime.combine(instance.until.date(), instance.start.time())
