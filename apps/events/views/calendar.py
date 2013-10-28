MODULE = __import__(__name__)

from django.http import Http404, HttpResponse
from django.template import TemplateDoesNotExist
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from time import gmtime, time
from events.models import *
from events.functions import format_to_mimetype
from events.templatetags import widgets

import settings


def calendar_widget(request, calendar, year, month):
    """
    Outputs calendar widget html via http response
    """
    calendar = get_object_or_404(Calendar, slug=calendar)

    try: # Convert applicable arguments to integer
        year = int(year) if year is not None else year
        month = int(month) if month is not None else month
    except ValueError:
        raise Http404

    html = widgets.calendar_widget(calendar, year, month)
    return HttpResponse(html)


def calendar(request, calendar, format=None):
    """
    Main calendar page, displaying an aggregation of events such as upcoming
    events, featured events, etc.
    """
    calendar = get_object_or_404(Calendar, slug=calendar)
    start = date.today()
    end = start + timedelta(days=settings.CALENDAR_MAIN_DAYS)
    events = calendar.range_event_instances(
        start,
        end
    ).order_by('start', 'event__title')

    template = 'events/frontend/calendar/event-list/listing.' + (format or 'html')
    context = {
        'now': date.today(),
        'calendar': calendar,
        'events': events,
    }

    try:
        return direct_to_template(request, template, context, mimetype=format_to_mimetype(format))
    except TemplateDoesNotExist:
        raise Http404


def event(request, calendar, instance_id, format=None):
    """
    Event instance page that serves as the public interface for events.
    """
    calendar = get_object_or_404(Calendar, slug=calendar)
    try:
        event = calendar.event_instances.get(pk=instance_id)
    except EventInstance.DoesNotExist:
        raise Http404

    format = format or 'html'
    template = 'events/frontend/event/event.' + format
    context = {
        'calendar': calendar,
        'event': event,
    }

    try:
        return direct_to_template(request, template, context, mimetype=format_to_mimetype(format))
    except TemplateDoesNotExist:
        raise Http404


def listing(request, calendar, start, end, format=None, extra_context=None):
    """
    Outputs a listing of events defined by a calendar and a range of dates.
    Format of this list is controlled by the optional format argument, ie. html,
    rss, json, etc.
    """
    calendar = get_object_or_404(Calendar, slug=calendar)
    events = calendar.range_event_instances(start, end)
    events = events.order_by('start')
    template = 'events/frontend/calendar/event-list/listing.' + (format or 'html')

    context = {
        'start': start,
        'end': end,
        'format': format,
        'calendar': calendar,
        'events': events,
    }

    if extra_context is not None:
        context.update(extra_context)
    try:
        return direct_to_template(request, template, context, mimetype=format_to_mimetype(format))
    except TemplateDoesNotExist:
        raise Http404


def auto_listing(request, calendar, year=None, month=None, day=None, format=None, extra_context=None):
    """
    Generates an event listing for the defined, year, month, day, or today.
    """
    # Default if no date is defined
    if year is month is day is None:
        return todays_listing(request, calendar)

    try:  # Convert applicable arguments to integer
        year = int(year) if year is not None else year
        month = int(month) if month is not None else month
        day = int(day) if day is not None else day
    except ValueError:
        raise Http404

    # Define start and end dates
    try:
        start = datetime(year, month or 1, day or 1)

        if month is None:
            end = datetime(year + 1, 1, 1)
        elif day is None:
            roll = month > 11  # Check for December to January rollover
            end = datetime(
                year + 1 if roll else year,
                month + 1 if not roll else 1,
                1
            )
            if type(extra_context) is not dict:
                extra_context = dict()
            if 'list_title' not in extra_context:
                extra_context['list_title'] = start.strftime("%B %Y")
        else:
            end = start + timedelta(days=1) - timedelta(seconds=1)
    except ValueError:
        raise Http404

    return listing(request, calendar, start, end, format, extra_context)


def week_listing(request, calendar, year, month, day, format=None):
    """
    Outputs a listing of the weeks event that the defined day belongs to.
    """
    try:  # Convert applicable arguments to integer
        year = int(year) if year is not None else year
        month = int(month) if month is not None else month
        day = int(day) if day is not None else day
    except ValueError:
        raise Http404

    try:
        day = datetime(year, month, day)
    except ValueError:
        raise Http404

    start = day - timedelta(days=day.weekday())
    end = start + timedelta(weeks=1)
    return listing(request, calendar, start, end, format, {
        'list_title': 'Events on Week of %s %s' % (start.strftime("%B"), start.day),
    })


def named_listing(request, calendar, type, format=None):
    """
    Handles named event listings, such as today, this-month, or this-year.
    """
    f = {
        'today': todays_listing,
        'tomorrow': tomorrows_listing,
        'this-month': months_listing,
        'this-week': weeks_listing,
        'this-year': years_listing,
    }.get(type, None)
    if f is not None:
        return f(request, calendar, format)
    raise Http404


def range_listing(request, calendar, start, end, format=None):
    """
    Generates an event listing for the date ranges provided through start
    and end.
    """
    from datetime import datetime
    date = lambda d: datetime(*[int(i) for i in d.split('-')])
    start = date(start)
    end = date(end) + timedelta(days=1) - timedelta(seconds=1)
    return listing(request, calendar, start, end, format, {
        'list_title': 'Events on %s %s through %s %s' % (
            start.strftime("%B"), start.day,
            end.strftime("%B"), end.day,
        ),
    })


def todays_listing(request, calendar, format=None):
    """
    Generates event listing for the current day
    """
    now = gmtime()
    year, month, day = now.tm_year, now.tm_mon, now.tm_mday
    return auto_listing(request, calendar, year, month, day, format, {
        'list_title': 'Today',
    })


def tomorrows_listing(request, calendar, format=None):
    """
    Generates event listing for tomorrows events
    """
    now = gmtime(time() + 86400)
    year, month, day = now.tm_year, now.tm_mon, now.tm_mday
    return auto_listing(request, calendar, year, month, day, format, {
        'list_title': 'Tomorrow',
    })


def weeks_listing(request, calendar, format=None):
    """
    Generates an event list for this weeks events
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(weeks=1)
    return listing(request, calendar, start, end, format, {
        'list_title': 'Events This Week',
    })


def months_listing(request, calendar, format=None):
    """
    Generate event list for the current month
    """
    now = gmtime()
    year, month, day = now.tm_year, now.tm_mon, None
    return auto_listing(request, calendar, year, month, day, format, {
        'list_title': 'Events This Month',
        'list_type': 'month',
    })


def years_listing(request, calendar, format=None):
    """
    Generate event listing for this year
    """
    now = gmtime()
    year, month, day = now.tm_year, None, None
    return auto_listing(request, calendar, year, month, day, format, {
        'list_title': 'Events This Year',
        'list_type': 'year',
    })
