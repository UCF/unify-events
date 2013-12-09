from django.conf.urls.defaults import *
from django.conf import settings

from events.views.calendar import category


urlpatterns = patterns('events.views.category',
    # http://events.ucf.edu/tag/tag-name
    url(r'^(?P<category>[\w-]+)/(\.(?P<format>[\w]+))?$',
        view=category,
        name="category"
    ),
)
