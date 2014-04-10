from datetime import date
from datetime import datetime
import urllib
import copy

from dateutil.relativedelta import relativedelta
from dateutil import rrule
from django import template
from django.http import Http404
from django.template import Context
from django.template import loader
from django.conf import settings
from django.shortcuts import get_object_or_404
import itertools
from ordereddict import OrderedDict

from events.models import Calendar
from events.models import State
import calendar as calgenerator

register = template.Library()


@register.simple_tag
def calendar_widget(calendars, year, month, pk=None, day=None, is_manager=0, size='small', use_pagers=True):

    # Catch requests for frontend widget with no specified calendar
    if calendars is "" and is_manager is 0:
        raise Http404

    if pk:
        calendars = get_object_or_404(Calendar, pk=pk)

    if day is None or day is "":
        relative_day = None
    else:
        if isinstance(day, datetime):
            relative_day = day.date()
        elif isinstance(day, date):
            relative_day = day
        else:
            raise TypeError('day must be a datetime.date or datetime.datetime, not a %s' % type(day))

    # Get this month, next and last month (1st day of month)
    if relative_day is None:
        this_month = date(int(year), int(month), 1)
    else:
        this_month = date(relative_day.year, relative_day.month, 1)
    next_month = date((this_month + relativedelta(months=+1)).year, (this_month + relativedelta(months=+1)).month, 1)
    last_month = date((this_month + relativedelta(months=-1)).year, (this_month + relativedelta(months=-1)).month, 1)

    # Create new list of days in month (strip week grouping)
    this_month_cal = list(itertools.chain.from_iterable(calgenerator.Calendar(settings.FIRST_DAY_OF_WEEK).monthdatescalendar(this_month.year, this_month.month)))

    # Set dates as dict keys. Use OrderedDict to sort by date.
    this_month_cal = OrderedDict((v, []) for k, v in enumerate(this_month_cal))

    # Create map of month and day/event list.
    month_calendar_map = dict({this_month: this_month_cal})

    # Get a date range by which we will fetch events
    start = this_month_cal.keys()[0]
    end = datetime.combine(this_month_cal.keys()[-1], datetime.max.time())

    # Fetch posted events within our date range.
    calendar = None
    events = list()
    if (isinstance(calendars, Calendar)):
        events.extend(calendars.range_event_instances(start, end).filter(event__state=State.get_id('posted')))
        calendar = calendars
    else:
        for cal in calendars:
            events.extend(cal.range_event_instances(start, end).filter(event__state=State.get_id('posted')))

    # Assign event to all days the event falls on.
    for event in events:
        if event.start.date() is not event.end.date():
            duration = rrule.rrule(rrule.DAILY, dtstart=event.start.date(), until=event.end.date())
            for day in duration:
                # Reassign instance day/times when using the larger widget
                if size != 'small':
                    event_by_day = copy.deepcopy(event)
                    all_day_on_day = False

                    # Set all-day event instance datetimes in a duration.
                    # All day events should have 00:00 as start time and 23:59 as end time.
                    if event.start.date() != day.date() and event.end.date() != day.date():
                        all_day_on_day = True
                        event_by_day.start = datetime.combine(day, datetime.min.time())
                        event_by_day.end = datetime.combine(day, datetime.max.time())
                    # Set the last day's start time in a duration
                    elif event.start.date() != day.date() and event.end.date() == day.date() and not event.parent:
                        event_by_day.start = datetime.combine(day, datetime.min.time())
                        event_by_day.end = datetime.combine(day, datetime.time(event_by_day.end))

                    if day.date() in month_calendar_map[this_month].keys():
                        if all_day_on_day:
                            month_calendar_map[this_month][day.date()][:0] = [event_by_day]
                        else:
                            month_calendar_map[this_month][day.date()].append(event_by_day)
                else:
                    month_calendar_map[this_month][day.date()].append(event)
        else:
            if event.start.date() in month_calendar_map[this_month].keys():
                month_calendar_map[this_month][event.start.date()].append(event)

    # Resort the map's events for each day if they've been modified.
    if size != 'small':
        for day in month_calendar_map[this_month].items():
            if day[1]:
                day[1].sort(key=lambda x: (x.start.time(), x.end.time()))


    context = {
        'MEDIA_URL': settings.MEDIA_URL,
        'is_manager': is_manager,
        'calendar': calendar,
        'this_month': this_month,
        'next_month': next_month,
        'last_month': last_month,
        'today': date.today(),
        'relative': relative_day,
        'calendar_map': month_calendar_map,
        'use_pagers': use_pagers,
    }

    if size == 'small':
        template = loader.get_template('events/widgets/calendar-sidebar.html')
    else:
        template = loader.get_template('events/widgets/calendar-large.html')

    html = template.render(Context(context))

    return html


@register.simple_tag
def pager(paginator, current_page):
    """
    Creates Bootstrap pagination links for a Paginator.
    Page range is 10.
    """
    # Account for paginator.Page passed as paginator object
    # TODO: remove this when CBVs w/pagination are converted
    if 'paginator' in paginator.__dict__:
        paginator = paginator.paginator

    range_length = 10
    if range_length > paginator.num_pages:
        range_length = paginator.num_pages

    # Calculate range of pages to return
    range_length -= 1
    range_min = max(paginator.count - (range_length / 2), 1)
    range_max = min(paginator.count + (range_length / 2), paginator.num_pages)
    range_diff = range_max - range_min
    if range_diff < range_length:
        shift = range_length - range_diff
        if range_min - shift > 0:
            range_min -= shift
        else:
            range_max += shift

    page_range = range(range_min, range_max + 1)

    # If current_page is not set, set it to 1
    if not current_page:
        current_page = 1
    else:
        current_page = int(current_page)

    context = {
        'range': page_range,
        'paginator': paginator,
        'current_page': current_page
    }

    template = loader.get_template('events/widgets/pager.html')
    html = template.render(Context(context))

    return html


@register.simple_tag
def feed_btns(url):
    """
    Generates feed buttons (ics/json/rss/xml) based off of a given URL.
    """
    if url.endswith('/') == False:
        url = url + '/'

    context = {
        'url': url
    }

    template = loader.get_template('events/widgets/feed-btns.html')
    html = template.render(Context(context))

    return html


@register.simple_tag
def social_btns(url, page_title):
    """
    Generates social sharing buttons based off of a given URL.
    """
    context = {
        'url': url,
        'page_title': page_title,
        'tweet_title': urllib.quote_plus('UCF Events: ' + page_title)
    }

    template = loader.get_template('events/widgets/social-btns.html')
    html = template.render(Context(context))

    return html