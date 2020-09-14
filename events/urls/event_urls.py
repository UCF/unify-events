from django.conf.urls import url

from events.views.event_views import EventDetailView


urlpatterns = [
    # https://events.ucf.edu/event/20404/football-ucf-at-fsu
    # https://events.ucf.edu/event/20404/football-ucf-at-fsu/feed.rss
    url(r'^(?P<pk>[\d]+)/(?P<slug>[\w-]+)/(?:feed\.(?P<format>[\w]+))?$',
        EventDetailView.as_view(),
        name='events.views.event_views.event'
    ),
]
