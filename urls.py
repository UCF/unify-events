from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView

from events.views.event_views import DayEventsListView

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^manager/', include('events.urls.manager')),
    url(r'^calendar/', include('events.urls.calendar')),
    url(r'^event/', include('events.urls.event_urls')),
    url(r'^category/', include('events.urls.category')),
    url(r'^tag/', include('events.urls.tag')),
    url(r'^(feed\.(?P<format>[\w]+))?$', DayEventsListView.as_view(), kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK}, name='home'),
    url(r'^help/$', TemplateView.as_view(template_name='events/static/help.html'), name='help'),
    url(r'for-developers/$', TemplateView.as_view(template_name='events/static/for-developers.html'), name='for-developers'),
    # TODO: production-ready static file delivery
    url(r'^tools/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT + '/events-widget/'}),
    url(r'^calendar-widget/(?P<view>[\w-]+)/(?P<size>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/$', TemplateView.as_view(template_name='events/widgets/calendar-by-url.html'), name='calendar-widget'),
    url(r'^calendar-widget/(?P<view>[\w-]+)/(?P<pk>\d+)/(?P<calendar_slug>[\w-]+)/(?P<size>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/$', TemplateView.as_view(template_name='events/widgets/calendar-by-url.html'), name='calendar-widget-by-calendar'),
    url(r'^calendar-widget/(?P<view>[\w-]+)/(?P<calendar_slug>[\w-]+)/(?P<size>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/$', TemplateView.as_view(template_name='events/widgets/calendar-by-url.html'), name='calendar-widget-by-calendar'),

    # Currently not using https://github.com/mrfunyon/django-esi because of such a small subset of alternate urls
    url(r'^esi/template/(?P<path>.*)', view='core.views.esi_template', name='esi-template'),
    url(r'^esi/event/(?P<pk>\d+)/template/(?P<path>.*)', view='core.views.esi_event', name='esi-event'),
)

handler500 = TemplateView.as_view(template_name='events/static/500.html')
handler404 = TemplateView.as_view(template_name='events/static/404.html')

if settings.SEARCH_ENABLED:
    urlpatterns += patterns('',
        url(r'^search/', include('haystack.urls')),
    )
else:
    urlpatterns += patterns('',
        url(r'^search/', DayEventsListView.as_view(), kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK}, name='haystack_search'),
    )

# TODO: if settings.DEBUG:
urlpatterns += patterns('',
    (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
        'django.views.static.serve',
        {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes' : True,
        }
    ),
)
