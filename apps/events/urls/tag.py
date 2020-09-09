from django.conf.urls import url

from events.views.event_views import EventsByTagList


urlpatterns = [
    # https://events.ucf.edu/tag/tag-name
    url(r'^(?P<tag_pk>\d+)/(?P<tag>[\w-]+)/(?:feed\.(?P<format>[\w]+))?$',
        view=EventsByTagList.as_view(),
        name='events.views.tag.tag'
    ),
]
