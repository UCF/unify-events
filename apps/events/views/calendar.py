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
from dateutil.relativedelta import relativedelta
from ordereddict import OrderedDict

import settings


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
    template = 'events/frontend/event-single/event.' + format
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
    # Check for GET params (backwards compatibility with old events widget)
    param_format = request.GET.get('format', '')
    param_limit = request.GET.get('limit', '')
    param_calendar = request.GET.get('calendar_id', '')
    param_monthwidget = request.GET.get('monthwidget', '')
    param_iswidget = request.GET.get('is_widget', '')

    # Get specified calendar. GET param will override any
    # previously defined calendar.
    if param_calendar != '':
        calendar = get_object_or_404(Calendar, id=param_calendar)
    else:
        calendar = get_object_or_404(Calendar, slug=calendar)

    events = calendar.range_event_instances(start, end)
    events = events.order_by('start')

    # Narrow down events by limit, if necessary.
    if param_limit != '':
        try:
            events = events[:param_limit]
        except:
            pass

    # Modify format value. GET param will override any
    # previously defined format.
    if param_format != '':
        format = param_format

    if param_iswidget == 'true':
        if param_monthwidget == 'true':
            template = 'events/frontend/calendar/listing/listing-widget-month.html'
        else:
            template = 'events/frontend/calendar/listing/listing-widget-list.html'
    else:
        template = 'events/frontend/calendar/listing/listing.' + (format or 'html')

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

    if type(extra_context) is not dict:
        extra_context = dict()

    # Define start and end dates
    try:
        start = datetime(year, month or 1, day or 1)

        if month is None:
            end = datetime(year + 1, 1, 1)
            if 'list_type' not in extra_context:
                extra_context['list_type'] = 'year'
            if 'list_title' not in extra_context:
                    extra_context['list_title'] = 'Events by Year: %s' % (year)
            if 'all_years' not in extra_context:
                extra_context['all_years'] = range(2009, (date.today() + relativedelta(years=+2)).year)
            if 'all_months' not in extra_context:
                extra_context['all_months'] = range(1, 13)
        elif day is None:
            roll = month > 11  # Check for December to January rollover
            end = datetime(
                year + 1 if roll else year,
                month + 1 if not roll else 1,
                1
            )
            if 'list_type' not in extra_context:
                extra_context['list_type'] = 'month'
            if 'list_title' not in extra_context:
                extra_context['list_title'] = 'Events by Month: %s' % (start.strftime("%B %Y"))
            if 'all_months' not in extra_context:
                extra_context['all_months'] = OrderedDict([
                    ('January', '01'),
                    ('February', '02'),
                    ('March', '03'),
                    ('April', '04'),
                    ('May', '05'),
                    ('June', '06'),
                    ('July', '07'),
                    ('August', '08'),
                    ('September', '09'),
                    ('October', '10'),
                    ('November', '11'),
                    ('December', '12')
                ])
            if 'all_years' not in extra_context:
                extra_context['all_years'] = range(2009, (date.today() + relativedelta(years=+2)).year)
        else:
            end = start + timedelta(days=1) - timedelta(seconds=1)
    except ValueError:
        raise Http404

    return listing(request, calendar, start, end, format, extra_context)


def calendar(request, calendar, format=None):
    """
    Main calendar page, displaying an aggregation of events such as upcoming
    events, featured events, etc.
    """
    start = date.today()
    end = start + timedelta(days=settings.CALENDAR_MAIN_DAYS)
    return listing(request, calendar, start, end, format, {
        'list_title': 'Events This Week',
    })


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


def day_listing(request, calendar, year, month, day, format=None):
    """
    Generates event listing for any single day
    """
    # Default if no date is defined
    if year is month is day is None:
        year = date.now().year
        month = date.now().month
        day = date.now().day

    return auto_listing(request, calendar, year, month, day, format, {
        'list_title': 'Events by Day',
        'list_type': 'day',
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


def tag(request, tag, calendar=None, format=None):
    """
    Page that lists all upcoming events tagged with a specific tag.
    Events can optionally be filtered by calendar.

    TODO: move this view?
    """
    # FUN TIMES: doing a deep relationship filter to event__tags__name__in fails.
    # https://github.com/alex/django-taggit/issues/84
    parent_events = Event.objects.filter(tags__name__in=[tag])
    events = EventInstance.objects.filter(event__in=parent_events, end__gt=datetime.now())
    if calendar:
        calendar = get_object_or_404(Calendar, slug=calendar)
        events = events.filter(event__calendar=calendar)
    else:
        events = events.filter(event__created_from__isnull=True)

    format = format or 'html'
    template = 'events/frontend/tag/tag.' + format
    context = {
        'tag': tag,
        'calendar': calendar,
        'events': events,
        'format': format,
    }

    try:
        return direct_to_template(request, template, context, mimetype=format_to_mimetype(format))
    except TemplateDoesNotExist:
        raise Http404


def category(request, category, calendar=None, format=None):
    """
    Page that lists all upcoming events categorized with the
    given category.
    Events can optionally be filtered by calendar.

    TODO: move this view?
    """
    category = get_object_or_404(Category, slug=category)
    events = EventInstance.objects.filter(event__category=category.id)
    if calendar:
        calendar = get_object_or_404(Calendar, slug=calendar)
        events = events.filter(event__calendar=calendar)
    else:
        events = events.filter(event__created_from__isnull=True)

    format = format or 'html'
    template = 'events/frontend/category/category.' + format
    context = {
        'category': category,
        'calendar': calendar,
        'events': events,
        'format': format,
    }

    try:
        return direct_to_template(request, template, context, mimetype=format_to_mimetype(format))
    except TemplateDoesNotExist:
        raise Http404