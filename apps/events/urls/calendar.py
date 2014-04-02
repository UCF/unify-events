from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls import url

from events.views.calendar import named_listing
from events.views.calendar import range_listing
from events.views.calendar import DayEventsListView
from events.views.calendar import EventsByCategoryList
from events.views.calendar import EventsByTagList
from events.views.calendar import EventDetailView
from events.views.calendar import MonthEventsListView
from events.views.calendar import WeekEventsListView
from events.views.calendar import YearEventsListView


urlpatterns = patterns('events.views.calendar',
    # http://events.ucf.edu/calendar/athletics/event-20404/football-ucf-at-fsu
    # http://events.ucf.edu/calendar/athletics/event-20404/football-ucf-at-fsu.rss
    url(r'^(?P<calendar>[\w-]+)/event-(?P<pk>[\d]+)/([\w-]+/)?(?P<format>[\w]+)?$',
        EventDetailView.as_view(),
        name='event'
    ),

    # http://events.ucf.edu/calendar/athletics
    # http://events.ucf.edu/calendar/athletics/2010.json
    # http://events.ucf.edu/calendar/athletics/2010/01
    # http://events.ucf.edu/calendar/athletics/2010/01/10.rss
    url(r'^(?P<calendar>[\w-]+)/(?P<format>[\w]+)?$', view=DayEventsListView.as_view(), name='calendar'),
    url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<format>[\w]+)?$', YearEventsListView.as_view(), name="year-listing"),
    url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<format>[\w]+)?$', MonthEventsListView.as_view(), name="month-listing"),
    url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(?P<format>[\w]+)?$', DayEventsListView.as_view(), name="day-listing"),
    url(r'^(?P<calendar>[\w-]+)/week-of/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(?P<format>[\w]+)?$', WeekEventsListView.as_view(), name='week-listing'),

    # TODO replace with list view?
    # http://events.ucf.edu/calendar/athletics/from/2010-01-02/to/2010-02-02
    url(r'^(?P<calendar>[\w-]+)/from/(?P<start>[\w-]+)/to/(?P<end>[\w-]+)/(?P<format>[\w]+)?$',
        view=range_listing,
        name="range-listing"
    ),

    # http://events.ucf.edu/calendar/athletics/this-year
    # http://events.ucf.edu/calendar/athletics/today
    # etc.
    url(r'^(?P<calendar>[\w-]+)/(?P<type>[\w-]+)/(?P<format>[\w]+)?$',
        view=named_listing,
        name="named-listing"
    ),

    # http://events.ucf.edu/calendar/athletics/tag/tag-name
    url(r'^(?P<calendar>[\w-]+)/tag/(?P<tag>[\w-]+)/(?P<format>[\w]+)?$',
        view=EventsByTagList.as_view(),
        name='tag-by-calendar'
    ),

    # http://events.ucf.edu/calendar/athletics/category/category-name
    url(r'^(?P<calendar>[\w-]+)/category/(?P<category>[\w-]+)/(?P<format>[\w]+)?$',
        view=EventsByCategoryList.as_view(),
        name='category-by-calendar'
    ),
)
