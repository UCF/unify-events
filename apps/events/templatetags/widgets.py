from datetime import date
from datetime import datetime
from dateutil import rrule
import calendar as calgenerator
import itertools

from django import template
from django.template import Context
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.datastructures import SortedDict
from django.conf import settings
from dateutil.relativedelta import relativedelta
from ordereddict import OrderedDict

from events.models import Calendar

register = template.Library()


@register.simple_tag
def calendar_widget(calendars, day=None, is_manager=0):

    if day is None or day is "":
        relative_day = date.today()
    else:
        if isinstance(day, datetime):
            relative_day = day.date()
        elif isinstance(day, date):
            relative_day = day
        else:
            raise TypeError('day must be a datetime.date or datetime.datetime, not a %s' % type(day))

    # Get next and last month (1st day of month)
    this_month = date(relative_day.year, relative_day.month, 1)
    next_month = date((this_month + relativedelta(months=+1)).year, (this_month + relativedelta(months=+1)).month, 1)
    last_month = date((this_month + relativedelta(months=-1)).year, (this_month + relativedelta(months=-1)).month, 1)
    months = list([last_month, this_month, next_month])

    # Create new lists of days in each month (strip week grouping)
    this_month_cal = list(itertools.chain.from_iterable(calgenerator.Calendar(0).monthdatescalendar(this_month.year, this_month.month)))
    next_month_cal = list(itertools.chain.from_iterable(calgenerator.Calendar(0).monthdatescalendar(next_month.year, next_month.month)))
    last_month_cal = list(itertools.chain.from_iterable(calgenerator.Calendar(0).monthdatescalendar(last_month.year, last_month.month)))

    # Set dates as dict keys. Use OrderedDict to sort by date.
    this_month_cal = OrderedDict((v, []) for k, v in enumerate(this_month_cal))
    next_month_cal = OrderedDict((v, []) for k, v in enumerate(next_month_cal))
    last_month_cal = OrderedDict((v, []) for k, v in enumerate(last_month_cal))

    # Create map using SortedDict to maintain declared order.
    month_calendar_map = SortedDict([(last_month, last_month_cal), (this_month, this_month_cal), (next_month, next_month_cal)])


    # Get a date range by which we will fetch events
    start = last_month_cal.keys()[0]
    end = next_month_cal.keys()[-1]

    # Fetch events; group them by date
    calendar = None
    events = list()
    if (isinstance(calendars, Calendar)):
        events.extend(calendars.range_event_instances(start, end).order_by('start'))
        calendar = calendars
    else:
        for cal in calendars:
            events.extend(cal.range_event_instances(start, end).order_by('start'))

    for event in events:
        # Assign event to all days the event falls on
        rule = rrule.rrule(rrule.DAILY, dtstart=event.start, until=event.end)
        for event_date in rule:
            for key in months:
                if event_date.date() in month_calendar_map[key].keys():
                    month_calendar_map[key][event_date.date()].append(event)


    template = loader.get_template('events/widgets/calendar.html')
    html = template.render(Context(
        {
            'MEDIA_URL': settings.MEDIA_URL,
            'is_manager': is_manager,
            'calendar': calendar,
            'this_month': this_month,
            'next_month': next_month,
            'last_month': last_month,
            'today': date.today(),
            'relative': relative_day,
            'cals': month_calendar_map,
        }
    ))

    return html
