from django import template
from django.template import loader, Context
from django.utils.safestring import mark_safe
from django.conf import settings

from datetime import datetime, date, timedelta
from events.functions import get_date_event_map, chunk

register = template.Library()

@register.simple_tag
def calendar_widget(calendar, year=None, month=None):
    
    if year is None or month is None:
        today = date.today()
        year = today.year
        month = today.month

    # Find date range for the passed month, year combo.  End is defined by
    # the start of next month minus 1 second.
    start = datetime(year, month, 1)
    end = datetime(year if month != 12 else year + 1,
                   month + 1 if month != 12 else 1,
                   1) - timedelta(seconds=1)

    events = calendar.range_event_instances(start, end).order_by('start')

    # Getting next and last month makes the assumption that moving 45 days
    # from the start or 15 days before start will result in next and last
    # month dates, so start needs to be the start of this month or this needs
    # to change
    this_month = start
    next_month = start + timedelta(days=45)
    last_month = start - timedelta(days=15)

    dates, date_event_map = get_date_event_map(events)

    # These tuples map to the difference between sunday or saturday for start
    # and end of the calendar page respectively.  So if the start of this month
    # is monday, we need to get 1 extra day before it, and the end of this month
    # is wednesday, we need to get 3 extra days after it.
    start_shift = (1, 2, 3, 4, 5, 6, 0)
    end_shift = (5, 4, 3, 2, 1, 0, 6)

    # Discover month's page start and end including previous and next month days
    cal_start = start - timedelta(days=start_shift[start.weekday()])
    cal_end = end + timedelta(days=end_shift[end.weekday()])

    # Generate a list of weeks and the days/events contained
    diff = cal_end - cal_start + timedelta(days=1)
    days = list()
    for d in range(0, diff.days):
        d = cal_start + timedelta(days=d)
        events = date_event_map.get(d.date(), None)
        if events is None:
            weight = ''
        else:
            weight = 'hasevents'

        # Filter out dates not in this month.  Ongoing events will cause the
        # calendar widget to display improperly by including any days that occur
        # for that event before the start of the month.  Adding an empty weight
        # fixes this.
        if d.date().month != month:
            days.append((d, events, 'muted'))
        else:
            days.append((d, events, weight))

    weeks = chunk(days, 7)
    template = loader.get_template('events/widgets/calendar.html')
    html = template.render(Context(
        {
            'MEDIA_URL': settings.MEDIA_URL,
            'calendar': calendar,
            'this_month': date(this_month.year, this_month.month, 1),
            'next_month': date(next_month.year, next_month.month, 1),
            'last_month': date(last_month.year, last_month.month, 1),
            'today': date.today(),
            'weeks': weeks,
        }
    ))

    return html