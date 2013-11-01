from django.views.generic.simple import direct_to_template
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^manager/', include('events.urls.manager')),
    url(r'^calendar/', include('events.urls.calendar')),
    url(r'^tag/', include('events.urls.tag')),
    url(r'^category/', include('events.urls.category')),
    url(r'^$', view='events.views.calendar.calendar', kwargs={'calendar': settings.FRONT_PAGE_CALENDAR_SLUG}),
    url(r'^help/$', direct_to_template, {'template': 'events/static/help.html'}, name='help'),
    url(r'for-developers/$', direct_to_template, {'template': 'events/static/for-developers.html'}, name='for-developers'),
    url(r'^tools/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT + '/events-widget/'}),
)

handler500 = lambda r: direct_to_template(r, template='500.html')
handler404 = lambda r: direct_to_template(r, template='404.html')

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
            'django.views.static.serve',
            {
                'document_root': settings.MEDIA_ROOT,
                'show_indexes' : True,
            }
        ),
    )