from django.conf.urls.defaults import *
from django.conf import settings
from events.views.calendar import auto_listing
from events.views.calendar import calendar
from events.views.calendar import calendar_widget
from events.views.calendar import event
from events.views.calendar import named_listing
from events.views.calendar import range_listing
from events.views.calendar import week_listing

cache_length = getattr(settings, 'CACHE_LENGTH', 60 * 15)

urlpatterns = patterns('events.views.calendar',
    # http://events.ucf.edu/calendar/athletics/event-20404/football-ucf-at-fsu
    # http://events.ucf.edu/calendar/athletics/event-20404/football-ucf-at-fsu.rss
    url(r'^(?P<calendar>[\w-]+)/event-(?P<instance_id>[\d]+)/([\w-]+/)?(\.(?P<format>[\w]+))?$', view=event, name='event'),

    # http://events.ucf.edu/calendar/athletics
    # http://events.ucf.edu/calendar/athletics/2010.json
    # http://events.ucf.edu/calendar/athletics/2010/01
    # http://events.ucf.edu/calendar/athletics/2010/01/10.rss
    url(r'^(?P<calendar>[\w-]+)/(\.(?P<format>[\w]+))?$', view=calendar, name="calendar"),
    url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(\.(?P<format>[\w]+))?$', view=auto_listing, name="year-listing"),
    url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(\.(?P<format>[\w]+))?$', view=auto_listing, name="month-listing"),
    url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(\.(?P<format>[\w]+))?$', view=auto_listing, name="day-listing"),
    url(r'^(?P<calendar>[\w-]+)/week-of/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(\.(?P<format>[\w]+))?$', view=week_listing, name='week-listing'),

    # http://events.ucf.edu/calendar/athletics/from/2010-01-02/to/2010-02-02
    url(r'^(?P<calendar>[\w-]+)/from/(?P<start>[\w-]+)/to/(?P<end>[\w-]+)/(\.(?P<format>[\w]+))?$', view=range_listing, name="range-listing"),

    # http://events.ucf.edu/calendar/athletics/this-year
    # http://events.ucf.edu/calendar/athletics/today
    # etc.
    url(r'^(?P<calendar>[\w-]+)/(?P<type>[\w-]+)/(\.(?P<format>[\w]+))?$', view=named_listing, name="named-listing"),

    # http://events.ucf.edu/calendar/athletics/2010/01/calendar-widget
    url(r'^(?P<calendar>[\w-]+)/widget/(?P<year>[\d]+)/(?P<month>[\d]+)/$', view=calendar_widget, name="calendar-widget"),
)
