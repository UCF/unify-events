from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView

from events.views.event_views import DayEventsListView
import urls

admin.autodiscover()

urlpatterns = patterns('',
    (r'^events/', include(urls.baseurlpatterns)),
)

handler500 = urls.handler500
handler404 = urls.handler404

if settings.SEARCH_ENABLED:
    urlpatterns += patterns('',
        url(r'^events/search/', include('haystack.urls')),
    )
else:
    urlpatterns += patterns('',
        url(r'^events/search/', DayEventsListView.as_view(), kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK}, name='haystack_search'),
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
