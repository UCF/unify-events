from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView

from events.views.event_views import DayEventsListView
from . import urls

admin.autodiscover()

urlpatterns = ['',
    (r'^events/', include(urls.baseurlpatterns)),
]

handler500 = urls.handler500
handler404 = urls.handler404

urlpatterns += [
    url(r'^events/search/', DayEventsListView.as_view(), kwargs={'pk': settings.FRONT_PAGE_CALENDAR_PK}, name='search_view'),
]
