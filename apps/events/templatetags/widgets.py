from datetime import date
from datetime import datetime
from datetime import timedelta
import calendar as calgenerator
import itertools
import collections

from django import template
from django.template import Context
from django.template import loader
from django.utils.safestring import mark_safe
from django.conf import settings
from dateutil.relativedelta import relativedelta

from events.functions import chunk
from events.functions import get_date_event_map
from events.models import Calendar

register = template.Library()


@register.simple_tag
def calendar_widget(calendars, day=None, is_manager=0):

    if day is None:
        relative_day = date.today()
    else:
        relative_day = day

    year = relative_day.year
    month = relative_day.month

    # Find date range for the passed month, year combo.  End is defined by
    # the start of next month minus 1 second.
    start = datetime(year, month, 1)
    end = datetime(year if month != 12 else year + 1,
                   month + 1 if month != 12 else 1,
                   1) - timedelta(seconds=1)

    calendar = None
    events = list()
    if (isinstance(calendars, Calendar)):
        events.extend(calendars.range_event_instances(start, end).order_by('start'))
        calendar = calendars
    else:
        for cal in calendars:
            events.extend(cal.range_event_instances(start, end).order_by('start'))

    # Getting next and last month makes the assumption that moving 45 days
    # from the start or 15 days before start will result in next and last
    # month dates, so start needs to be the start of this month or this needs
    # to change
    #this_month = start
    #next_month = start + timedelta(days=45)
    #last_month = start - timedelta(days=15)

    this_month = date(start.year, start.month, 1)
    next_month = this_month + relativedelta(months=+1)
    last_month = this_month + relativedelta(months=-1)

    # Create new lists of days in each month (strip week grouping)
    this_month_cal = list(itertools.chain.from_iterable(calgenerator.Calendar(0).monthdatescalendar(this_month.year, this_month.month)))
    next_month_cal = list(itertools.chain.from_iterable(calgenerator.Calendar(0).monthdatescalendar(next_month.year, next_month.month)))
    last_month_cal = list(itertools.chain.from_iterable(calgenerator.Calendar(0).monthdatescalendar(last_month.year, last_month.month)))

    # Set dates as dict keys
    this_month_cal = collections.OrderedDict((v, []) for k, v in enumerate(this_month_cal))
    next_month_cal = collections.OrderedDict((v, []) for k, v in enumerate(next_month_cal))
    last_month_cal = collections.OrderedDict((v, []) for k, v in enumerate(last_month_cal))

    month_calendar_map = dict({last_month.month: last_month_cal, this_month.month: this_month_cal, next_month.month: next_month_cal})


    for event in events:
        month_calendar_map[event.start.month][event.start.date()].append(event)


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