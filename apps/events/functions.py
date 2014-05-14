from events.models import Event
from events.models import State


def get_date_event_map(events):
    """Get a tuple containing a list of dates and a mapping between those dates
    and the events that occur on them."""
    from datetime import date
    date_event_map = dict()
    dates = list()

    # Create date and event mapping
    for event in events:
        day = date(*(event.start.year, event.start.month, event.start.day))

        if day not in dates:
            dates.append(day)
            date_event_map[day] = list()

        date_event_map[day].append(event)

    return dates, date_event_map


def chunk(i, c_size):
    """Split an interable into even sized chunks defined by c_size.  If the
    number of items in the iterable cannot be evenly divided by c_size, the
    remainder will fall into the final element."""
    import math
    chunks = int(math.ceil(len(i) / float(c_size)))
    return [i[c * c_size : c * c_size + c_size] for c in range(0, chunks)]


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
