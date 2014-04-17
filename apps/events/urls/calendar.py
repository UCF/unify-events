from django.conf.urls import patterns
from django.conf.urls import url

from events.views.event_views import named_listing
from events.views.event_views import DayEventsListView
from events.views.event_views import EventsByCategoryList
from events.views.event_views import EventsByTagList
from events.views.event_views import MonthEventsListView
from events.views.event_views import WeekEventsListView
from events.views.event_views import YearEventsListView


urlpatterns = patterns('events.views.event_views',
    # http://events.ucf.edu/calendar/athletics
    # http://events.ucf.edu/calendar/athletics/2010/feed.json
    # http://events.ucf.edu/calendar/athletics/2010/01
    # http://events.ucf.edu/calendar/athletics/2010/01/10/feed.rss
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/(?:feed\.(?P<format>[\w]+))?$', view=DayEventsListView.as_view(), name='calendar'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/(?P<year>[\d]+)/(?:feed\.(?P<format>[\w]+))?$', YearEventsListView.as_view(), name='year-listing'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?:feed\.(?P<format>[\w]+))?$', MonthEventsListView.as_view(), name='month-listing'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(?:feed\.(?P<format>[\w]+))?$', DayEventsListView.as_view(), name='day-listing'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/week-of/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(?:feed\.(?P<format>[\w]+))?$', WeekEventsListView.as_view(), name='week-listing'),

    # http://events.ucf.edu/calendar/athletics/this-year
    # http://events.ucf.edu/calendar/athletics/today
    # etc.
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/(?P<type>[\w-]+)/(?:feed\.(?P<format>[\w]+))?$',
        view=named_listing,
        name='named-listing'
    ),

    # http://events.ucf.edu/calendar/athletics/tag/tag-name
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/tag/(?P<tag_pk>\d+)/(?P<tag>[\w-]+)/(?:feed\.(?P<format>[\w]+))?$',
        view=EventsByTagList.as_view(),
        name='tag-by-calendar'
    ),

    # http://events.ucf.edu/calendar/athletics/category/category-name
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/category/(?P<category_pk>\d+)/(?P<category>[\w-]+)/(?:feed\.(?P<format>[\w]+))?$',
        view=EventsByCategoryList.as_view(),
        name='category-by-calendar'
    ),
)
