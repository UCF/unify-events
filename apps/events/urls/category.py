from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls import url

from events.views.calendar import category


urlpatterns = patterns('events.views.category',
    # http://events.ucf.edu/tag/tag-name
    url(r'^(?P<category>[\w-]+)/(\.(?P<format>[\w]+))?$',
        view=category,
        name="category"
    ),
)
