import bleach
import HTMLParser

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

        # Check to see if the event needs to be Created/Posted for any subscribed calendars
        for subscribed_calendar in event.calendar.subscribed_calendars.all():
            try:
                copied = subscribed_calendar.events.get(created_from=event)
            except Event.DoesNotExist:
                # Does not exist so import the event
                subscribed_calendar.import_event(event)
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