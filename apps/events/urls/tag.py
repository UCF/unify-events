from django.conf.urls.defaults import *
from django.conf import settings

from events.views.calendar import tag


urlpatterns = patterns('events.views.tag',
    # http://events.ucf.edu/tag/tag-name
    url(r'^(?P<tag>[\w-]+)/(\.(?P<format>[\w]+))?$',
        view=tag,
        name="tag"
    ),
)