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
from django.views.generic import View
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


class CalendarEventsListView(MultipleFormatTemplateViewMixin, ListView):
    """
    Generic events listing view based on the start date and end date.
    """
    model = EventInstance
    context_object_name = 'event_instances'
    template_name = 'events/frontend/calendar/calendar.'
    list_type = None
    day = None
    month = None
    year = None
    start_date = None
    end_date = None
    list_title = None
    calendar = None

    def is_js_widget(self):
        """
        Determine whether or not the view should accomodate for JS Widget-related
        query parameters and manipulate the view accordingly.
        """
        if self.request.GET.get('is_widget') == 'true':
            return True
        return False

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

        # Backwards compatibility with JS Widget
        if self.is_js_widget():
            limit = self.request.GET.get('limit')
            if limit and self.request.GET.get('monthwidget') != 'true':
                self.paginate_by = int(limit)

        self.queryset = events
        return events

    def get_calendar(self):
        """
        Get the calendar based on the url parameter 'calendar'.
        """
        # Backwards compatibility with JS Widget and UNL events system urls.
        # Use 'calendar_id' query param if is_js_widget() is true or if the
        # current calendar is the front page calendar (i.e. we're at www.ucf.edu/events/)
        # and the 'calendar_id' query param is set.
        if self.is_js_widget() or self.request.GET.get('calendar_id') is not None and self.kwargs.get('calendar') == settings.FRONT_PAGE_CALENDAR_SLUG:
            calendar = get_object_or_404(Calendar, pk=self.request.GET.get('calendar_id'))
        else:
            calendar = self.calendar

        if calendar is None:
            calendar_slug = self.kwargs.get('calendar')
            args = self.kwargs
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
        if not start_date:
            # Backwards compatibility with JS Widget
            if self.is_js_widget():
                # Attempt to set start_date as the 1st day of the month with the 
                # params provided.  Default list widget should set start_date to now.
                if self.request.GET.get('monthwidget') == 'true':
                    year = self.request.GET.get('year', datetime.now().year)
                    month = self.request.GET.get('month', datetime.now().month)
                    if year and month:
                        year = int(year)
                        month = int(month)
                        start_date = datetime(year, month, 1)
                    else:
                        start_date = datetime.now()
                        start_date = datetime.combine(datetime(start_date.year, start_date.month, 1), datetime.max.time())
                else:
                    start_date = datetime.now()
            else:
                day_month_year = self.get_day_month_year()
                start_date = datetime(day_month_year[2], day_month_year[1] or 1, day_month_year[0] or 1)
            
            self.start_date = start_date

        return start_date

    def get_end_date(self):
        """
        Returns the end date or creates an end date based on the url parameters.
        """
        end_date = self.end_date
        if not end_date:
            # Backwards compatibility with JS Widget
            if self.is_js_widget():
                start_date = self.get_start_date()
                # Set end date to last day of the month (relative to start_date) for
                # monthwidget.  Just use +1 month from start_date for default list widget.
                if self.request.GET.get('monthwidget') == 'true':
                    end_date = datetime(start_date.year, start_date.month, 1) + relativedelta(months=1) - timedelta(days=1)
                    end_date = datetime.combine(end_date, datetime.max.time())
                else:
                    end_date = start_date + relativedelta(months=1)

        return end_date

    def get_context_data(self, **kwargs):
        """
        Main calendar page, displaying an aggregation of events such as upcoming
        events, featured events, etc.
        """
        context = super(CalendarEventsListView, self).get_context_data(**kwargs)
        context['list_title'] = self.list_title
        context['calendar'] = self.get_calendar()
        context['start'] = self.get_start_date()
        context['end'] = self.get_end_date()
        context['list_type'] = self.list_type

        # Backwards compatibility with JS Widget
        context['param_limit'] = self.request.GET.get('limit')
        context['param_calendar'] = self.request.GET.get('calendar_id')
        context['param_monthwidget'] = self.request.GET.get('monthwidget')
        context['param_iswidget'] = self.request.GET.get('is_widget')
        context['param_month'] = self.request.GET.get('month')
        context['param_year'] = self.request.GET.get('year')

        return context

    def get_template_names(self):
        if self.is_js_widget():
            if self.request.GET.get('monthwidget') == 'true':
                return ['events/frontend/calendar/calendar-type/calendar-widget-month.html']
            else:
                return ['events/frontend/calendar/calendar-type/calendar-widget-list.html']
        else:
            return super(CalendarEventsListView, self).get_template_names()


class DayEventsListView(CalendarEventsListView):
    """
    Events listing for a day.
    """
    paginate_by = 25
    list_title = 'Events by Day'
    list_type = 'day'

    def is_upcoming(self):
        """
        Check for a url query param of 'upcoming' for backwards compatibility
        with UNL events system url structure
        """
        if self.request.GET.get('upcoming') is not None and self.get_start_date().date() == datetime.now().date():
            return True
        return False

    def get_queryset(self):
        # Backwards compatibility with old events system
        # (Accomodate for requests to "../?upcoming=upcoming")
        if self.is_upcoming():
            calendar = self.get_calendar()
            events = calendar.future_event_instances().order_by('start')
            self.paginate_by = 25
            self.list_type = 'upcoming'
            self.queryset = events
            return events
        else:
            return super(DayEventsListView, self).get_queryset()

    def get_end_date(self):
        """
        Returns the end date that is one day past today.
        """
        end_date = super(DayEventsListView, self).get_end_date()
        if not end_date:
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

        # Backwards compatibility with old events system
        # (Accomodate for requests to "../?upcoming=upcoming")
        if self.is_upcoming():
            context['list_title'] = 'Upcoming Events'
        else:
            if start_date.date() == datetime.today().date():
                context['list_title'] = 'Today\'s Events'
            elif start_date.date() == (datetime.today() + timedelta(days=1)).date():
                context['list_title'] = 'Tomorrow\'s Events'

        return context


class WeekEventsListView(CalendarEventsListView):
    """
    Events listing for a week.
    """
    paginate_by = 25
    list_title = 'Events by Week'
    list_type = 'week'

    def get_start_date(self):
        """
        Returns the start of the week as the start date.
        """
        start_date = self.start_date
        if not start_date:
            start_date = super(WeekEventsListView, self).get_start_date()
            start_date = start_date - timedelta(days=start_date.weekday())
            self.start_date = start_date

        return start_date

    def get_end_date(self):
        """
        Returns the end date that is one day past today.
        """
        start_date = self.get_start_date()
        end_date = datetime.combine(start_date + timedelta(weeks=1), datetime.max.time())
        self.end_date = end_date

        return end_date

    def get_context_data(self, **kwargs):
        """
        Dynamically set the list title for the week
        """
        context = super(WeekEventsListView, self).get_context_data(**kwargs)
        start_date = self.get_start_date()
        end_date = self.get_end_date()
        if start_date <= datetime.now() and end_date >= datetime.now():
            context['list_title'] = 'Events This Week.'
        else:
            context['list_title'] = 'Events on Week of %s %s' % (start_date.strftime("%B"), start_date.day)

        return context


class MonthEventsListView(CalendarEventsListView):
    """
    Events listing for a month.
    """
    list_type = 'month'
    list_title = 'Events This Month.'

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
        now = datetime.now()
        if start_date.month != now.month or start_date.year != now.year:
            context['list_title'] = 'Events by Month: %s' % (start_date.strftime("%B %Y"))

        if 'all_months' not in context:
                context['all_months'] = OrderedDict([
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
        if 'all_years' not in context:
            context['all_years'] = range(2009, (date.today() + relativedelta(years=+2)).year)

        return context


class YearEventsListView(CalendarEventsListView):
    """
    Events listing for a year.
    """
    list_type = 'year'
    list_title = 'Events This Year.'

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
        if start_date.year != datetime.now().year:
            context['list_title'] = 'Events by Year: %s' % (start_date.strftime("%B %Y"))

        if 'all_years' not in context:
            context['all_years'] = range(2009, (date.today() + relativedelta(years=+2)).year)
        if 'all_months' not in context:
            context['all_months'] = range(1, 13)

        return context


class UpcomingEventsListView(CalendarEventsListView):
    """
    Events listing for a calendar's upcoming events with
    no specified range (return up to the 'paginate_by' value.)
    """
    paginate_by = 25
    list_type = 'upcoming'
    list_title = 'Upcoming Events'

    def get_queryset(self):
        """
        Get all future events.
        """
        calendar = self.get_calendar()
        events = calendar.future_event_instances().order_by('start')

        self.queryset = events
        return events


def named_listing(request, calendar, type, format=None):
    """
    Handles named event listings, such as today, this-month, or this-year.
    """
    c = {
        'today': DayEventsListView,
        'tomorrow': DayEventsListView,
        'this-week': WeekEventsListView,
        'this-month': MonthEventsListView,
        'this-year': YearEventsListView,
        'upcoming': UpcomingEventsListView,
    }.get(type, None)
    if c is not None:
        today = datetime.today()
        day = today.day
        month = today.month
        year = today.year

        if c == MonthEventsListView or c == YearEventsListView:
            day = None

        if c == YearEventsListView:
            month = None

        view = c.as_view(day=day, month=month, year=year)
        return view(request, calendar=calendar, format=format)
    raise Http404


# TODO replace with Class Based Views
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
