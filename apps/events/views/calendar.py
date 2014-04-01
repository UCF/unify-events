MODULE = __import__(__name__)

from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.http import Http404, HttpResponse
from django.template import TemplateDoesNotExist
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.utils.decorators import classonlymethod

from time import gmtime, time
from events.models import *
from core.utils import format_to_mimetype
from core.views import MultipleFormatTemplateViewMixin
from events.templatetags import widgets
from dateutil.relativedelta import relativedelta
from ordereddict import OrderedDict

import settings


class EventDetailView(MultipleFormatTemplateViewMixin, DetailView):
    context_object_name = 'event_instance'
    model = EventInstance
    template_name = 'events/frontend/event-single/event.'


def listing(calendar, start, end):
    """
    Get events for the given calendar within the given time range.
    """
    calendar = get_object_or_404(Calendar, slug=calendar)

    events = calendar.range_event_instances(start, end)
    events = events.order_by('start')

    return events


def auto_listing(calendar, year=None, month=None, day=None):
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
        else:
            end = start + timedelta(days=1) - timedelta(seconds=1)
    except ValueError:
        raise Http404

    return listing(calendar, start, end)


class CalendarEventsListView(MultipleFormatTemplateViewMixin, ListView):
    """
    Generic events listing view based on the start date and end date.
    """

    model = EventInstance
    context_object_name = 'event_instances'
    template_name = 'events/frontend/calendar/calendar.'

    day = None
    month = None
    year = None
    start_date = None
    end_date = None
    list_title = None
    calendar = None

    def get_queryset(self):
        """
        Get events for the given day. If no day is provide then
        return the current day's events.
        """
        start_date = self.get_start_date()
        end_date = self.get_end_date()
        calendar = self.get_calendar()
        events = calendar.range_event_instances(start_date, end_date)
        events = events.order_by('start')
        self.queryset =  events
        return events

    def get_calendar(self):
        """
        Get the calendar based on the url parameter 'calendar'.
        """
        calendar = self.calendar
        if calendar is None:
            calendar_slug = self.kwargs.get('calendar')
            if calendar_slug is None:
                # Value is none return right away since no calendar was provided.
                return calendar_slug
            else:
                calendar = get_object_or_404(Calendar, slug=calendar_slug)

            self.calendar = calendar

        return calendar

    def _get_date_by_parameter(self, param):
        """
        Use get_day_month_year to these values.
        Returns the date values (int) from url parameters.
        """
        if param in ['day', 'month', 'year']:
            date_value = getattr(self, param)
            if date_value is None:
                date_param = self.kwargs.get(param)
                if date_param is None:
                    # Value is None so return right away no date url parameter was provided.
                    return date_param
                else:
                    date_value = int(date_param)

                setattr(self, param, date_value)
            return date_value
        else:
            raise AttributeError('Param is not a date parameter (day, month, or year).')

    def get_day_month_year(self):
        """
        Return a tuple of day, month and year. Return current day
        if no url parameters are provided.
        """
        day = self._get_date_by_parameter('day')
        month = self._get_date_by_parameter('month')
        year = self._get_date_by_parameter('year')

        if day is month is year is None:
            # Default to current day if nothing is provided
            self.day = day = datetime.now().day
            self.month = month = datetime.now().month
            self.year = year = datetime.now().year

        return (day, month, year)

    def get_start_date(self):
        """
        Returns the start date or creates an start date based on the url parameters.
        """
        start_date = self.start_date
        if not self.start_date:
            day_month_year = self.get_day_month_year()
            start_date = datetime(day_month_year[2], day_month_year[1] or 1, day_month_year[0] or 1)
            self.start_date = start_date
        return start_date

    def get_end_date(self):
        """
        Returns the end date or creates an end date based on the url parameters.
        """
        if self.end_date:
            end_date = self.end_date
        else:
            raise ImproperlyConfigured("'%s' must define 'end_date'"
                                       % self.__class__.__name__)

        return end_date

    def get_context_data(self, **kwargs):
        """
        Main calendar page, displaying an aggregation of events such as upcoming
        events, featured events, etc.
        """
        context = super(CalendarEventsListView, self).get_context_data(**kwargs)
        context['list_title'] = self.list_title
        context['calendar'] = get_object_or_404(Calendar, slug=self.kwargs['calendar'])
        context['start'] = self.get_start_date()
        context['end'] = self.get_end_date()
        return context


class DayEventsListView(CalendarEventsListView):
    """
    Events listing for a day.
    """

    list_title = 'Events by Day'

    def get_end_date(self):
        """
        Returns the end date that is one day past today.
        """
        start_date = self.get_start_date()
        end_date = start_date + timedelta(days=1) - timedelta(seconds=1)
        self.end_date = end_date

        return end_date

    def get_context_data(self, **kwargs):
        """
        Overrides the list title if the events are from today.
        """
        context = super(DayEventsListView, self).get_context_data(**kwargs)
        start_date = self.get_start_date()

        if start_date.date() == datetime.today().date():
            context['list_title'] = 'Today\'s Events'
        elif start_date.date() == (datetime.today() + timedelta(days=1)).date():
            context['list_title'] = 'Tomorrow\'s Events'

        return context


class WeekEventsListView(CalendarEventsListView):
    """
    Events listing for a week.
    """

    def get_end_date(self):
        """
        Returns the end date that is one day past today.
        """
        start_date = self.get_start_date()
        end_date = start_date + timedelta(weeks=1)
        self.end_date = end_date

        return end_date

    def get_context_data(self, **kwargs):
        """
        Dynamically set the list title for the week
        """
        context = super(WeekEventsListView, self).get_context_data(**kwargs)
        raise Exception
        start_date = self.get_start_date()
        context['list_title'] = 'Events on Week of %s %s' % (start_date.strftime("%B"), start_date.day)

        return context


class MonthEventsListView(CalendarEventsListView):
    """
    Events listing for a month.
    """

    def get_end_date(self):
        """
        Returns the end date that is one day past today.
        """
        start_date = self.get_start_date()
        day_month_year = self.get_day_month_year()
        day = day_month_year[0]
        month = day_month_year[1]
        year = day_month_year[2]

        roll = month > 11  # Check for December to January rollover
        end_date = datetime(
            year + 1 if roll else year,
            month + 1 if not roll else 1,
            1
        )
        self.end_date = end_date

        return end_date

    def get_context_data(self, **kwargs):
        """
        Dynamically set the list title for the week
        """
        context = super(MonthEventsListView, self).get_context_data(**kwargs)
        start_date = self.get_start_date()
        context['list_title'] = 'Events by Month: %s' % (start_date.strftime("%B %Y"))

        return context


class YearEventsListView(CalendarEventsListView):
    """
    Events listing for a year.
    """

    def get_end_date(self):
        """
        Returns the end date that is one day past today.
        """
        start_date = self.get_start_date()
        end_date = datetime(start_date.date().year + 1, 1, 1)
        self.end_date = end_date

        return end_date

    def get_context_data(self, **kwargs):
        """
        Dynamically set the list title for the week
        """
        context = super(YearEventsListView, self).get_context_data(**kwargs)
        start_date = self.get_start_date()
        context['list_title'] = 'Events by Year: %s' % (start_date.strftime("%B %Y"))

        return context


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
        'list_type': 'week',
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


def paginated_listing(request, template, context, format=None):
    """
    Generate a paginated list of events.
    """
    paginator = Paginator(context['events'], 20)
    page = request.GET.get('page', 1)
    try:
        context['events'] = paginator.page(page)
    except PageNotAnInteger:
        context['events'] = paginator.page(1)
    except EmptyPage:
        context['events'] = paginator.page(paginator.num_pages)

    try:
        return TemplateView.as_view(request, template, context, mimetype=format_to_mimetype(format))
    except TemplateDoesNotExist:
        raise Http404


class EventsByTagList(MultipleFormatTemplateViewMixin, ListView):
    """
    Page that lists all upcoming events tagged with a specific tag.
    Events can optionally be filtered by calendar.

    TODO: move this view?
    """
    context_object_name = 'events'
    model = Event
    paginate_by = 25
    template_name = 'events/frontend/tag/tag.'

    def get_context_data(self, **kwargs):
        context = super(EventsByTagList, self).get_context_data()
        context['tag'] = self.kwargs['tag']
        return context

    def get_queryset(self):
        kwargs = self.kwargs
        tag = kwargs['tag']
        events = EventInstance.objects.filter(event__tags__name__in=[tag])

        if 'calendar' not in kwargs:
            calendar = None
        else:
            calendar = get_object_or_404(Calendar, slug=self.kwargs['calendar'])

        if calendar:
            events = events.filter(event__calendar=calendar)
        else:
            events = events.filter(event__created_from__isnull=True)

        return events


class EventsByCategoryList(MultipleFormatTemplateViewMixin, ListView):
    """
    Page that lists all upcoming events categorized with a specific tag.
    Events can optionally be filtered by calendar.

    TODO: move this view?
    """
    context_object_name = 'events'
    model = Event
    paginate_by = 25
    template_name = 'events/frontend/category/category.'

    def get_context_data(self, **kwargs):
        context = super(EventsByCategoryList, self).get_context_data()
        context['category'] = get_object_or_404(Category, slug=self.kwargs['category'])
        return context

    def get_queryset(self):
        kwargs = self.kwargs
        category = kwargs['category']
        events = EventInstance.objects.filter(event__category__slug=category)

        if 'calendar' not in kwargs:
            calendar = None
        else:
            calendar = get_object_or_404(Calendar, slug=self.kwargs['calendar'])

        if calendar:
            events = events.filter(event__calendar=calendar)
        else:
            events = events.filter(event__created_from__isnull=True)

        return events
