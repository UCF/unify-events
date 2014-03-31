from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls import url

from events.views.calendar import category
from events.views.calendar import EventsByCategoryList


urlpatterns = patterns('events.views.category',
    # http://events.ucf.edu/tag/tag-name
    url(r'^(?P<category>[\w-]+)/?$',
        view=EventsByCategoryList.as_view(),
        name='category'
    ),
)
