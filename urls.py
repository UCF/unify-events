from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from events.models import Calendar
from events.views.event_views import named_listing
from events.views.event_views import DayEventsListView
from events.views.event_views import HomeEventsListView
from events.views.event_views import MonthEventsListView
from events.views.event_views import WeekEventsListView
from events.views.event_views import YearEventsListView

if settings.SEARCH_ENABLED:
    from haystack.views import search_view_factory
    from events.views.search import GlobalSearchView

admin.autodiscover()

baseurlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^manager/', include('events.urls.manager')),
    url(r'^calendar/', include('events.urls.calendar')),
    url(r'^event/', include('events.urls.event_urls')),
    url(r'^category/', include('events.urls.category')),
    url(r'^tag/', include('events.urls.tag')),
    url(r'^help/$', TemplateView.as_view(template_name='events/static/help.html'), name='help'),
    url(r'for-developers/$', TemplateView.as_view(template_name='events/static/for-developers.html'), name='for-developers'),
    # TODO: production-ready static file delivery
    url(r'^tools/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT + '/events-widget/'}),
    url(r'^calendar-widget/(?P<view>[\w-]+)/(?P<size>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/$', TemplateView.as_view(template_name='events/widgets/calendar-by-url.html'), name='calendar-widget'),
    url(r'^calendar-widget/(?P<view>[\w-]+)/(?P<pk>\d+)/(?P<calendar_slug>[\w-]+)/(?P<size>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/$', TemplateView.as_view(template_name='events/widgets/calendar-by-url.html'), name='calendar-widget-by-calendar'),
    url(r'^calendar-widget/(?P<view>[\w-]+)/(?P<calendar_slug>[\w-]+)/(?P<size>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/$', TemplateView.as_view(template_name='events/widgets/calendar-by-url.html'), name='calendar-widget-by-calendar'),
    url(r'^esi/template/(?P<path>.*)', view='core.views.esi_template', name='esi-template'),
    url(r'^esi/(?P<model_name>[\w-]+)/(?P<object_id>[\d]+)/(calendar/(?P<calendar_id>[\d]+)/)?(?P<template_name>.*)', view='core.views.esi')
)


# Add static file location for debug
baseurlpatterns += staticfiles_urlpatterns()
urlpatterns = patterns('',
    (r'^', include(baseurlpatterns)),
)


# Append search urls (this MUST go before Main Calendar overrides; else a 404 is returned on the haystack_search view!)
if settings.SEARCH_ENABLED:
    urlpatterns += patterns('haystack.views',
        url(r'^search/$', search_view_factory(
            view_class=GlobalSearchView,
            template='search/search.html'
        ), name='haystack_search'),
    )
else:
    urlpatterns += patterns('',
        url(r'^search/', DayEventsListView.as_view(), kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK}, name='haystack_search'),
    )


# Get Main Calendar so we have access to its slug:
main_calendar = Calendar.objects.get(pk=settings.FRONT_PAGE_CALENDAR_PK)

# Append Main Calendar url overrides
urlpatterns += patterns('',
    url(r'^(feed\.(?P<format>[\w]+))?$',
        HomeEventsListView.as_view(),
        kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK, 'slug': main_calendar.slug},
        name='home'
    ),
    url(r'^(?P<year>[\d]+)/(?:feed\.(?P<format>[\w]+))?$',
        YearEventsListView.as_view(),
        kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK, 'slug': main_calendar.slug},
        name='main-calendar-year-listing'
    ),
    url(r'^(?P<year>[\d]+)/(?P<month>[\d]+)/(?:feed\.(?P<format>[\w]+))?$',
        MonthEventsListView.as_view(),
        kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK, 'slug': main_calendar.slug},
        name='main-calendar-month-listing'
    ),
    url(r'^(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(?:feed\.(?P<format>[\w]+))?$',
        DayEventsListView.as_view(),
        kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK, 'slug': main_calendar.slug},
        name='main-calendar-day-listing'
    ),
    url(r'^week-of/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(?:feed\.(?P<format>[\w]+))?$',
        WeekEventsListView.as_view(),
        kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK, 'slug': main_calendar.slug},
        name='main-calendar-week-listing'
    ),
    url(r'^(?P<type>[\w-]+)/(?:feed\.(?P<format>[\w]+))?$',
        view=named_listing,
        kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK, 'slug': main_calendar.slug},
        name='main-calendar-named-listing'
    ),
)


# Error handling
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^debug/500-templ/$', TemplateView.as_view(template_name='500.html')),
        (r'^debug/404-templ/$', TemplateView.as_view(template_name='404.html')),
    )
