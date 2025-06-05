from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from events.models import Calendar
from events.views.event_views import named_listing
from events.views.event_views import DayEventsListView
from events.views.event_views import HomeEventsListView
from events.views.event_views import MonthEventsListView
from events.views.event_views import WeekEventsListView
from events.views.event_views import YearEventsListView
from events.views.event_views import CalendarWidgetView

import django_saml2_auth

import core

from events.views.search import GlobalSearchView

admin.autodiscover()

ROBOTS_TEMPLATE = ''

if settings.DEV_MODE:
    ROBOTS_TEMPLATE = 'robots.dev.txt'
else:
    ROBOTS_TEMPLATE = 'robots.prod.txt'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^robots.txt', TemplateView.as_view(template_name=ROBOTS_TEMPLATE, content_type='text/plain')),
    url(r'^manager/', include('events.urls.manager')),
    url(r'^calendar/', include('events.urls.calendar')),
    url(r'^event/', include('events.urls.event_urls')),
    url(r'^category/', include('events.urls.category')),
    url(r'^tag/', include('events.urls.tag')),
    url(r'^help/$', TemplateView.as_view(template_name='events/static/help.html'), name='help'),
    url(r'^calendar-widget/(?P<view>[\w-]+)/(?P<size>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/$', CalendarWidgetView.as_view(), name='calendar-widget'),
    url(r'^calendar-widget/(?P<view>[\w-]+)/calendar/(?P<pk>\d+)/(?P<calendar_slug>[\w-]+)/(?P<size>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/$', CalendarWidgetView.as_view(), name='calendar-widget-by-calendar'),
    url(r'^esi/template/(?P<path>.*)', view=core.views.esi_template, name='esi-template'),
    url(r'^esi/(?P<model_name>[\w-]+)/(?P<object_id>[\d]+)/(calendar/(?P<calendar_id>[\d]+)/)?(?P<template_name>.*)', view=core.views.esi)
]

# Append search urls
urlpatterns += [
    url(r'^search/(?:feed\.(?P<format>[\w]+))?$', GlobalSearchView.as_view(), name='search_view'),
]


try:
    # Get Main Calendar so we have access to its slug:
    main_calendar = Calendar.objects.get(pk=settings.FRONT_PAGE_CALENDAR_PK)

    # Append Main Calendar url overrides
    urlpatterns += [
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
    ]
except Exception:
    # An exception can occur here if the app db hasn't been set up yet.
    # Just skip registration of these URLs then
    pass

# Logins
if settings.USE_SAML:
    urlpatterns.insert(
        0,
        url(r'^sso/',
            include('django_saml2_auth.urls')
        )
    )
    urlpatterns.insert(
        1,
        url(r'^manager/login/$',
            django_saml2_auth.views.signin
        )
    )
    urlpatterns.insert(
        2,
        url(r'^admin/login/$',
            django_saml2_auth.views.signin
        )
    )


# Error handling
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

if settings.DEBUG:
    urlpatterns += [
        url(r'^debug/500-templ/$', TemplateView.as_view(template_name='500.html')),
        url(r'^debug/404-templ/$', TemplateView.as_view(template_name='404.html')),

    ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
