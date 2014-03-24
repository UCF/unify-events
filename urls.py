from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^manager/', include('events.urls.manager')),
    # url(r'^calendar/', include('events.urls.calendar')),
    # url(r'^tag/', include('events.urls.tag')),
    # url(r'^category/', include('events.urls.category')),
    # url(r'^$', view='events.views.calendar.calendar', kwargs={'calendar': settings.FRONT_PAGE_CALENDAR_SLUG}),
    url(r'^help/$', TemplateView.as_view(template_name='events/static/help.html'), name='help'),
    url(r'for-developers/$', TemplateView.as_view(template_name='events/static/for-developers.html'), name='for-developers'),
    # url(r'^tools/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT + '/events-widget/'}),
    # url(r'^calendar-widget/(?P<view>[\w-]+)/(?P<size>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/$', direct_to_template, {'template': 'events/widgets/calendar-by-url.html'}, name='calendar-widget'),
    # url(r'^calendar-widget/(?P<view>[\w-]+)/(?P<calendar_slug>[\w-]+)/(?P<size>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/$', direct_to_template, {'template': 'events/widgets/calendar-by-url.html'}, name='calendar-widget-by-calendar')
)

handler500 = TemplateView.as_view(template_name='events/static/500.html')
handler404 = TemplateView.as_view(template_name='events/static/404.html')

#if settings.DEBUG:
urlpatterns += patterns('',
    (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
        'django.views.static.serve',
        {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes' : True,
        }
    ),
)
