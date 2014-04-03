from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls import url

from events.views.event_views import EventsByTagList


urlpatterns = patterns('events.views.tag',
    # http://events.ucf.edu/tag/tag-name
    url(r'^(?P<tag>[\w-]+)/(feed\.(?P<format>[\w]+))?$',
        view=EventsByTagList.as_view(),
        name='tag'
    ),
)
