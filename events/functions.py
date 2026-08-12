import bleach
import calendar as calgenerator
from datetime import date
import html

from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Min, Q
from django.utils.formats import date_format

from events.models import Calendar
from events.models import Event
from events.models import State
from events.models import get_main_calendar


def update_subscriptions(event, is_main_rereview=False):
    """
    Update subscriptions based on originating event's state.
    """
    copied_events = event.duplicated_to.all()
    if event.state != State.posted:
        # If original event has a state other than POSTED, delete the duplicated events
        for copied_event in copied_events:
            copied_event.delete()
    else:
        # Updates the copied versions if the original event is updated
        for copied_event in copied_events:
            copy = copied_event.pull_updates(is_main_rereview)

        # Get the original event-- the event passed to this function might be a copy!
        if event.created_from:
            original_event = event.created_from
        else:
            original_event = event

        # Check to see if the event needs to be Created/Posted for any subscribed calendars
        for subscribed_calendar in event.calendar.subscribed_calendars.all():
            try:
                copied = subscribed_calendar.events.get(created_from=original_event)
            except Event.DoesNotExist:
                # Does not exist so import the event
                subscribed_calendar.import_event(original_event)
            except MultipleObjectsReturned:
                # Found multiple objects...should never happen but pass since
                # there is atleast one event copied don't do anything.
                pass


def remove_html(value):
    """
    Run Bleach on the given value because UNL Events doesn't do HTML sanitization on anything.

    Bleach here does NOT use the configuration settings in settings.py--it will remove
    ALL tags and attributes found.
    """
    if value:
        value = bleach.clean(value, tags=[], attributes={}, strip=True)
        html.unescape(value)
    return value


def get_valid_years():
    """
    Returns a range of valid year values for returning data.
    Useful when needing to prevent dynamically-generated data from
    expanding beyond an excessive amount of time.
    """
    this_year = date(date.today().year, 1, 1).year
    years = list(range(2009, this_year+3)) # add two years, plus 1 for last index
    return years


def get_earliest_valid_date(date_format=None):
    valid_years = get_valid_years()
    the_date = date(valid_years[0], 1, 1)
    if date_format:
        the_date = the_date.strftime(date_format)
    return the_date


def get_latest_valid_date(date_format=None):
    valid_years = get_valid_years()
    the_date = date(valid_years[-1], 12, calgenerator.monthrange(valid_years[-1], 12)[1])
    if date_format:
        the_date = the_date.strftime(date_format)
    return the_date


def is_date_in_valid_range(the_date):
    """
    Returns true or false if the date passed falls within a
    valid year range (as defined by get_valid_years()).
    """
    earliest_valid_date = get_earliest_valid_date()
    latest_valid_date = get_latest_valid_date()

    if the_date < earliest_valid_date or the_date > latest_valid_date:
        return False
    else:
        return True


def get_featurable_events():
    """
    Events that are eligible to be featured on the calendar home page.

    Only main calendar events can be featured, and only published ones: the
    card links straight to the event, so anything still pending would send
    visitors to a 404.

    The featured event form and its select2 endpoint both call this, so a user
    can never search up an event the form would then reject.
    """
    try:
        main_calendar = get_main_calendar()
    except Calendar.DoesNotExist:
        return Event.objects.none()

    return Event.objects.filter(
        calendar=main_calendar,
        state__in=State.get_published_states()
    ).annotate(
        # Two events can easily share a title, so the picker labels each one
        # with the date it next happens. Annotating it here keeps that off the
        # per-row query path when a page of search results is being labelled.
        next_start=Min(
            'event_instances__start',
            filter=Q(event_instances__start__gte=date.today())
        )
    ).order_by('title')


def format_featured_event_label(title, next_start):
    """
    Builds the text shown for one event in the featured event picker.

    Both the select2 endpoint and the widget that renders the already-selected
    event call this, so the label doesn't change out from under the user when
    the form is redisplayed.
    """
    if next_start is None:
        return title
    return '{0} — {1}'.format(title, date_format(next_start, 'N j, Y'))
