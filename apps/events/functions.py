import bleach
import calendar as calgenerator
from datetime import date
import HTMLParser

from django.core.exceptions import MultipleObjectsReturned

from events.models import Event
from events.models import State


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
        value = bleach.clean(value, tags=[], attributes={}, styles=[], strip=True)
        h = HTMLParser.HTMLParser()
        value = h.unescape(value)
    return value


def get_valid_years():
    """
    Returns a range of valid year values for returning data.
    Useful when needing to prevent dynamically-generated data from
    expanding beyond an excessive amount of time.
    """
    this_year = date(date.today().year, 1, 1).year
    years = range(2009, this_year+3) # add two years, plus 1 for last index
    return years


def is_date_in_valid_range(the_date):
    """
    Returns true or false if the date passed falls within a
    valid year range (as defined by get_valid_years()).
    """
    valid_years = get_valid_years()
    earliest_valid_date = date(valid_years[0], 1, 1)
    latest_valid_date = date(valid_years[-1], 12, calgenerator.monthrange(valid_years[-1], 12)[1])

    if the_date < earliest_valid_date or the_date > latest_valid_date:
        return False
    else:
        return True
