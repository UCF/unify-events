MODULE = __import__(__name__)

from datetime import date, timedelta

from dateutil import rrule
from dateutil.relativedelta import relativedelta
from django.db.models.query import QuerySet
from django.http import Http404
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from ordereddict import OrderedDict
from taggit.models import Tag

from events.models import *
from events.functions import get_valid_years
from events.functions import is_date_in_valid_range
from core.views import MultipleFormatTemplateViewMixin
from core.views import PaginationRedirectMixin
from core.views import InvalidSlugRedirectMixin
from settings_local import FIRST_DAY_OF_WEEK


class EventDetailView(InvalidSlugRedirectMixin, MultipleFormatTemplateViewMixin, DetailView):
    by_model = EventInstance
    context_object_name = 'event_instance'
    model = EventInstance
    template_name = 'events/frontend/event-single/event.'


class CalendarEventsBaseListView(ListView):
    model = EventInstance
    context_object_name = 'event_instances'
    paginate_by = 25
    calendar = None
    day = None
    month = None
    year = None
    start_date = None
    end_date = None

    def get_calendar(self):
        """
        Get the calendar based on the url parameter 'calendar'.
        """
        calendar = self.calendar

        if not calendar:
            pk = self.kwargs.get('pk')
            args = self.kwargs
            if pk is None:
                # Value is none return right away since no calendar was provided.
                return pk
            else:
                calendar = get_object_or_404(Calendar, pk=pk)

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
                    if (param in ['day', 'month'] and len(date_param) > 2) or (param == 'year' and len(date_param) > 4):
                        return date_param
                    else:
                        date_value = int(date_param)

                setattr(self, param, date_value)
            return date_value
        else:
            raise AttributeError('Param is not a date parameter (day, month, or year).')

    def is_date_selected(self):
        """
        Determine if a date was selected.
        """
        day = self.kwargs.get('day')
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')

        if day is month is year is None:
            return False
        else:
            return True

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
            day_month_year = self.get_day_month_year()
            try:
                if day_month_year[0] in xrange(1, 32) and day_month_year[1] in xrange(1, 13):
                    start_date = datetime(day_month_year[2] or 1, day_month_year[1] or 1, day_month_year[0] or 1)
                else:
                    raise Http404
            except ValueError:
                # Date is invalid; stop here
                raise Http404
            except TypeError:
                # Year param was passed as a string
                raise Http404

        self.start_date = start_date
        return start_date

    def get_end_date(self):
        """
        Return the end date.
        """
        return self.end_date

    def get_context_data(self, **kwargs):
        """
        Set the calendar in the context.
        """
        context = super(CalendarEventsBaseListView, self).get_context_data(**kwargs)
        context['calendar'] = self.get_calendar()
        context['start_date'] = self.get_start_date()
        context['end_date'] = self.get_end_date()
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Prevent dynamically generated pages from returning
        content from too far into the future or the past.
        This primarily exists to prevent google from crawling
        to infinity and beyond.
        """
        start_date = self.get_start_date().date()
        if is_date_in_valid_range(start_date):
            return super(CalendarEventsBaseListView, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404


class CalendarEventsListView(InvalidSlugRedirectMixin, MultipleFormatTemplateViewMixin, CalendarEventsBaseListView):
    """
    Generic events listing view for the frontend.
    """
    by_model = Calendar
    template_name = 'events/frontend/calendar/calendar.'
    list_type = None
    list_title = None

    def is_mapped_feed(self):
        """
        Determine if a feed should use map_event_range to map event instances in the
        returned queryset.  This is false by default and must be explicitly defined
        via the query param 'mapped_events=true'.
        """
        if self.get_format() != 'html' and self.request.GET.get('mapped_events') and self.request.GET.get('mapped_events').lower() == 'true':
            return True
        return False

    def get_queryset(self):
        """
        Get events for the given day. If no day is provided then
        return the current day's events.
        """
        start_date = self.get_start_date()
        end_date = self.get_end_date()
        calendar = self.get_calendar()
        events = calendar.range_event_instances(start_date, end_date).filter(event__state__in=State.get_published_states())
        if self.get_format() == 'html' or self.is_mapped_feed():
            events = map_event_range(start_date, end_date, events)
        else:
            events = events.filter(start__gte=start_date)

        self.queryset = events
        return events

    def get_context_data(self, **kwargs):
        """
        Main calendar page, displaying an aggregation of events such as upcoming
        events, featured events, etc.
        """
        context = super(CalendarEventsListView, self).get_context_data(**kwargs)
        context['list_title'] = self.list_title
        context['list_type'] = self.list_type

        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect all requests for main calendar list views.
        This exists primarily for preventing duplicate content issues
        for canonical urls.
        """
        calendar = self.get_calendar()
        url_name = request.resolver_match.url_name
        if calendar.is_main_calendar and 'main-calendar-' not in url_name and url_name != 'home':
            kwargs = request.resolver_match.kwargs
            kwargs.pop('pk', None)
            kwargs.pop('slug', None)
            if 'format' in kwargs and kwargs['format'] is None: # prevent feed.None from being passed into new redirect url
                kwargs.pop('format', None)

            if url_name == 'calendar':
                url_name = 'home'
            elif not 'main-calendar-' in url_name:
                url_name = 'main-calendar-' + url_name
            return HttpResponsePermanentRedirect(reverse(url_name, kwargs=kwargs))
        else:
            return super(CalendarEventsListView, self).dispatch(request, *args, **kwargs)


class DayEventsListView(PaginationRedirectMixin, CalendarEventsListView):
    """
    Events listing for a day.
    """
    paginate_by = 25
    list_title = 'Events by Day'
    list_type = 'day'

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
        start_date_str = start_date.strftime('%A, %B %d, %Y')

        if start_date.date() == datetime.today().date():
            context['list_title'] = 'Today\'s Events'
        elif start_date.date() == (datetime.today() + timedelta(days=1)).date():
            context['list_title'] = 'Tomorrow\'s Events'
        else:
            context['list_title'] = start_date_str

        return context


class HomeEventsListView(DayEventsListView):
    """
    Events listing for the home page (Today's events on the Main Calendar.)

    Contains various methods that add backwards compatibility with the
    UNL events system.
    """
    list_title = 'Today\'s Events'

    def is_js_widget(self):
        """
        Determine whether or not the view should accomodate for JS Widget-related
        query parameters and manipulate the view accordingly.
        """
        if self.request.GET.get('is_widget') and self.request.GET.get('is_widget').lower() == 'true':
            return True
        return False

    def is_js_feed(self):
        """
        Determine whether or not the view should accomodate for the 'format' query
        parameter (NOT kwarg).
        """
        if self.request.GET.get('format') and self.request.GET.get('format') in self.available_formats and self.get_format() != 'html':
            return True
        return False

    def is_upcoming(self):
        """
        Check for a url query param of 'upcoming' for backwards compatibility
        with UNL events system url structure
        """
        if self.request.GET.get('upcoming'):
            return True
        return False

    def is_event_instance(self):
        """
        Check for a url query param of 'eventdatetime_id' for backwards
        compatibility with UNL events system url structure
        """
        if self.request.GET.get('eventdatetime_id'):
            return True
        return False

    def is_alternate_calendar(self):
        """
        Check for a url query param of 'calendar_id' for backwards compatibility
        with UNL events system url structure
        """
        if self.request.GET.get('calendar_id'):
            return True
        return False

    def needs_fallback_redirect(self):
        if ((self.is_js_widget() == False and not self.is_js_feed()) and (self.is_upcoming() or self.is_event_instance() or self.is_alternate_calendar())):
            return True
        return False

    def get_calendar(self):
        """
        Overrides the calendar if requesting the JS widget.
        """
        if self.is_alternate_calendar():
            # Throw a 404 if calendar_id param was provided, but is invalid
            if self.request.GET.get('calendar_id').isdigit():
                pk = int(self.request.GET.get('calendar_id'))
            else:
                raise Http404
            calendar = get_object_or_404(Calendar, pk=pk)
        else:
            calendar = get_main_calendar()

        self.calendar = calendar
        return calendar

    def _get_date_by_parameter(self, param):
        """
        Checks param against self.kwargs or request.GET if
        requesting the JS widget.
        """
        if self.is_js_widget():
            if param in ['day', 'month', 'year']:
                date_value = getattr(self, param)
                if date_value is None:
                    # Check either kwargs or GET param for backwards compatibility
                    # with JS Widget
                    date_param = self.kwargs.get(param) or self.request.GET.get(param)
                    if date_param is None:
                        # Value is None so return right away no date url parameter was provided.
                        return date_param
                    else:
                        date_value = int(date_param)

                    setattr(self, param, date_value)
                return date_value
            else:
                raise AttributeError('Param is not a date parameter (day, month, or year).')
        else:
            return super(HomeEventsListView, self)._get_date_by_parameter(param)

    def get_start_date(self):
        """
        Overrides the start date if requesting the JS widget in month mode.
        """
        start_date = self.start_date
        if not start_date:
            start_date = super(HomeEventsListView, self).get_start_date()
            # Backwards compatibility with JS Widget
            # Attempt to set start_date as the 1st day of the month with the
            # params provided.
            if self.is_js_widget() and self.request.GET.get('monthwidget') == 'true':
                start_date = datetime(start_date.date().year, start_date.date().month, 1)

            self.start_date = start_date

        return start_date

    def get_end_date(self):
        """
        Overrides the end date if requesting the JS widget in month mode
        """
        end_date = super(HomeEventsListView, self).get_end_date()
        if not end_date:
            start_date = self.get_start_date()
            # Backwards compatibility with JS Widget
            # Set end date to last day of the month (relative to start_date) for monthwidget.
            if self.is_js_widget() and self.request.GET.get('monthwidget') == 'true':
                end_date = datetime(start_date.year, start_date.month, 1) + relativedelta(months=1) - timedelta(days=1)
                end_date = datetime.combine(end_date, datetime.max.time())
                self.end_date = end_date
            else:
                end_date = start_date + timedelta(days=1) - timedelta(seconds=1)
                self.end_date = end_date

        return end_date

    def get_queryset(self):
        """
        Get events for the given day. If no day is provided then
        return the current day's events.
        """
        start_date = self.get_start_date()
        end_date = self.get_end_date()
        calendar = self.get_calendar()

        # Backward compatibility with UNL events system.
        # Make sure upcoming feeds via ?upcoming=upcoming mimic UpcomingEventsListView!
        # Also used for js widget
        if self.is_js_widget() or (self.is_js_feed() and self.is_upcoming()):
            events = calendar.future_event_instances().filter(event__state__in=State.get_published_states(), start__gte=datetime.now())
        # Main Calendar Today HTML views and mapped feeds:
        elif not self.is_js_widget() and self.get_format() == 'html' or self.is_mapped_feed():
            events = calendar.range_event_instances(start_date, end_date).filter(event__state__in=State.get_published_states())
            events = map_event_range(start_date, end_date, events)
        # Main Calendar Today feeds (non-mapped):
        else:
            events = calendar.range_event_instances(start_date, end_date).filter(event__state__in=State.get_published_states(), start__gte=start_date)

        # Backwards compatibility with JS Widget
        if self.is_js_widget():
            limit = self.request.GET.get('limit')
            # Set a default limit if one is not provided
            if not limit or not limit.isdigit():
                limit = 5
            # Prevent really big limits
            if int(limit) > 25:
                limit = 25
            if limit and self.request.GET.get('monthwidget') != 'true':
                self.paginate_by = int(limit)

        self.queryset = events
        return events

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect 'upcoming', 'calendar_id' and 'eventdatetime_id' query param views for
        backward compatibility, if this is not a request for the js widget.

        Accomodates for optional 'format' param.
        """
        if self.needs_fallback_redirect():
            calendar = self.get_calendar()
            new_kwargs = {}
            new_url_name = ''

            if self.is_js_feed():
                new_kwargs['format'] = self.request.GET.get('format')

            if self.is_event_instance():
                """
                Try to fetch by eventdatetime_id (backward compatibility with UNL Events).

                Fetching by unl_eventdatetime_id should always return .count() > 1 with
                imported events that have been copied to other calendars (and/or the Main Calendar.)

                Assuming no calendar_id value is provided (which is typically the case), the
                Main Calendar version of the event will be prioritized.
                If a version on the Main Calendar doesn't exist, use the copy on the first
                calendar found.
                Otherwise, the original event will be fetched.

                If nothing with the eventdatetime_id is found, try searching by pk instead.
                """
                if self.request.GET.get('eventdatetime_id').isdigit():
                    instance_objects = EventInstance.objects.filter(unl_eventdatetime_id=self.request.GET.get('eventdatetime_id'))
                    instance = None
                    # Is this imported instance copied to multiple calendars?
                    if instance_objects.count() > 1:
                        instance = instance_objects.filter(event__calendar=calendar)
                        # Is this an event that has been copied to more than one calendar,
                        # but not from the calendar returned by self.get_calendar()?
                        # (We don't know which calendar to prioritize--try to fall back to *something*)
                        if instance.count() == 0:
                            instance = instance_objects[0]
                        # Instance was successfully filtered down to calendar returned by self.get_calendar().
                        else:
                            instance = instance[0]
                    # Is this imported event instance on exactly one calendar?
                    elif instance_objects.count() == 1:
                        instance = instance_objects[0]
                    # Is this a non-imported event instance?
                    elif instance_objects.count() == 0:
                        instance = get_object_or_404(EventInstance, pk=self.request.GET.get('eventdatetime_id'))

                    new_url_name = 'event'
                    new_kwargs['pk'] = instance.pk
                    new_kwargs['slug'] = instance.slug
                else:
                    raise Http404

            elif self.is_upcoming():
                new_kwargs['type'] = 'upcoming'
                if calendar.is_main_calendar:
                    new_url_name = 'main-calendar-named-listing'
                else:
                    new_url_name = 'named-listing'
                    new_kwargs['pk'] = calendar.pk
                    new_kwargs['slug'] = calendar.slug

            elif self.is_alternate_calendar():
                if calendar.is_main_calendar:
                    new_url_name = 'home'
                else:
                    new_kwargs['pk'] = calendar.pk
                    new_kwargs['slug'] = calendar.slug
                    new_url_name = 'calendar'

            return HttpResponsePermanentRedirect(reverse(new_url_name, kwargs=new_kwargs))

        else:
            return super(HomeEventsListView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if self.is_js_widget():
            if self.request.GET.get('monthwidget') == 'true':
                return ['events/frontend/calendar/calendar-type/calendar-widget-month.html']
            else:
                return ['events/frontend/calendar/calendar-type/calendar-widget-list.html']
        else:
            return super(HomeEventsListView, self).get_template_names()


class WeekEventsListView(PaginationRedirectMixin, CalendarEventsListView):
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
            relative_date = super(WeekEventsListView, self).get_start_date()
            if relative_date.weekday() == FIRST_DAY_OF_WEEK:
                start_date = relative_date
            else:
                start_date = relative_date + relativedelta(weekday=FIRST_DAY_OF_WEEK, weeks=-1)

            self.start_date = start_date
        return start_date

    def get_end_date(self):
        """
        Returns the end date that is one day past today.
        """
        start_date = self.get_start_date()
        end_date = datetime.combine(start_date + timedelta(days=6), datetime.max.time())
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
            context['list_title'] = 'Events This Week'
        else:
            context['list_title'] = 'Events on Week of %s %s, %s' % (start_date.strftime("%B"), start_date.day, start_date.year)

        return context


class MonthEventsListView(CalendarEventsListView):
    """
    Events listing for a month.
    """
    paginate_by = None # Don't paginate feed querysets (html view is handled via calendar_widget templatetag)
    list_type = 'month'
    list_title = 'Events This Month'

    def get_start_date(self):
        """
        Returns the start date or creates an start date based on the url parameters.
        """
        start_date = self.start_date
        if not start_date:
            day_month_year = self.get_day_month_year()
            try:
                if day_month_year[1] in xrange(1, 13):
                    start_date = datetime(day_month_year[2] or 1, day_month_year[1] or 1, day_month_year[0] or 1)
                else:
                    raise Http404
            except ValueError:
                # Date is invalid; stop here
                raise Http404
            except TypeError:
                # Year parameter was passed as a string
                raise Http404

        self.start_date = start_date
        return start_date

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
            context['all_years'] = get_valid_years()

        return context

    def get_queryset(self):
        """
        Avoid double queryset fetches (this view uses the calendar_widget templatetag,
        which does its own event instance query)
        """
        events = None
        if self.get_format() == 'html':
            events = list()
        else:
            events = super(MonthEventsListView, self).get_queryset()
        return events


class YearEventsListView(CalendarEventsListView):
    """
    Events listing for a year.
    """
    list_type = 'year'
    list_title = 'Events This Year'

    def get_start_date(self):
        """
        Returns the start date or creates an start date based on the url parameters.
        """
        start_date = self.start_date
        if not start_date:
            day_month_year = self.get_day_month_year()
            try:
                start_date = datetime(day_month_year[2] or 1, 1, 1) 
            except ValueError:
                # Date is invalid; stop here
                raise Http404
            except TypeError:
                # Year param was passed as a string
                raise Http404

        self.start_date = start_date
        return start_date

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
            context['list_title'] = 'Events by Year: %s' % (start_date.strftime("%Y"))

        if 'all_years' not in context:
            context['all_years'] = get_valid_years()
        if 'all_months' not in context:
            context['all_months'] = range(1, 13)

        return context

    def get_queryset(self):
        """
        Avoid double queryset fetches (this view uses the calendar_widget templatetag,
        which does its own event instance query)
        """
        return list()


class UpcomingEventsListView(PaginationRedirectMixin, CalendarEventsListView):
    """
    Events listing for a calendar's upcoming events with
    no specified range (return up to the 'paginate_by' value.)
    """
    paginate_by = 25
    list_type = 'upcoming'
    list_title = 'Upcoming Events'

    def get_queryset(self):
        """
        Get events that start after now. Using the function instead
        of using the self.queryset because apache may hold onto the
        datetime.now() value.
        """
        calendar = self.get_calendar()
        events = calendar.future_event_instances().filter(event__state__in=State.get_published_states(), start__gte=datetime.now())

        self.queryset = events

        return events


def named_listing(request, pk, slug, type, format=None):
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
        return view(request, pk=pk, slug=slug, format=format)
    raise Http404



class ListViewByCalendarMixin(object):
    def get_calendar(self):
        """
        Returns the calendar object specified for the view; if no calendar
        is specified, return the main calendar.
        """
        if 'pk' not in self.kwargs:
            calendar = get_main_calendar()
        else:
            calendar = get_object_or_404(Calendar, pk=self.kwargs['pk'])

        return calendar

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect all requests for main calendar list views.
        This exists primarily for preventing duplicate content issues
        for canonical urls.
        """
        calendar = self.get_calendar()
        url_name = request.resolver_match.url_name
        if calendar.is_main_calendar and '-by-calendar' in url_name:
            kwargs = request.resolver_match.kwargs
            kwargs.pop('pk', None)
            kwargs.pop('slug', None)
            if 'format' in kwargs and kwargs['format'] is None: # prevent feed.None from being passed into new redirect url
                kwargs.pop('format', None)

            url_name = url_name.replace('-by-calendar', '')
            return HttpResponsePermanentRedirect(reverse(url_name, kwargs=kwargs))
        else:
            return super(ListViewByCalendarMixin, self).dispatch(request, *args, **kwargs)


class EventsByTagList(InvalidSlugRedirectMixin, MultipleFormatTemplateViewMixin, PaginationRedirectMixin, ListViewByCalendarMixin, ListView):
    """
    Page that lists all upcoming events tagged with a specific tag.
    Events can optionally be filtered by calendar.
    """
    by_model = Tag
    context_object_name = 'event_instances'
    model = EventInstance
    paginate_by = 25
    template_name = 'events/frontend/tag/tag.'

    def get_context_data(self, **kwargs):
        context = super(EventsByTagList, self).get_context_data()
        context['tag'] = get_object_or_404(Tag, pk=self.kwargs['tag_pk'])
        context['calendar'] = self.get_calendar()

        return context

    def get_queryset(self):
        kwargs = self.kwargs
        tag_pk = kwargs['tag_pk']
        events = EventInstance.objects.filter(event__tags__pk=tag_pk,
                                              end__gte=datetime.now(),
                                              event__state__in=State.get_published_states()
                                              )

        calendar = self.get_calendar()
        events = events.filter(event__calendar=calendar)

        return events


class EventsByCategoryList(InvalidSlugRedirectMixin, MultipleFormatTemplateViewMixin, PaginationRedirectMixin, ListViewByCalendarMixin, ListView):
    """
    Page that lists all upcoming events categorized with a specific tag.
    Events can optionally be filtered by calendar.
    """
    by_model = Category
    context_object_name = 'event_instances'
    model = EventInstance
    paginate_by = 25
    template_name = 'events/frontend/category/category.'

    def get_context_data(self, **kwargs):
        context = super(EventsByCategoryList, self).get_context_data()
        context['category'] = get_object_or_404(Category, pk=self.kwargs['category_pk'])
        context['calendar'] = self.get_calendar()

        return context

    def get_queryset(self):
        kwargs = self.kwargs
        category_pk = kwargs['category_pk']
        events = EventInstance.objects.filter(event__category__pk=category_pk,
                                              end__gte=datetime.now(),
                                              event__state__in=State.get_published_states()
                                              )

        calendar = self.get_calendar()
        events = events.filter(event__calendar=calendar)

        return events


class CalendarWidgetView(TemplateView):
    """
    View that handles sidebar calendar widget and js widget requests.
    """
    template_name = 'events/widgets/calendar-by-url.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Prevent dynamically generated pages from returning
        content from too far into the future or the past.
        This primarily exists to prevent google from crawling
        to infinity and beyond.
        """
        try:
            start_date = date(int(self.kwargs.get('year')), int(self.kwargs.get('month')), 1)
        except ValueError:
            # Invalid date
            raise Http404
        if is_date_in_valid_range(start_date):
            return super(CalendarWidgetView, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404
