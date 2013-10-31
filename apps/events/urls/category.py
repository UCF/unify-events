from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page
from django.conf import settings
from events.views.calendar import category

cache_length = getattr(settings, 'CACHE_LENGTH', 60 * 15)

urlpatterns = patterns('events.views.category',
    # http://events.ucf.edu/tag/tag-name
    url(r'^(?P<category>[\w-]+)/(\.(?P<format>[\w]+))?$',
        view=cache_page(category, cache_length),
        name="category"
    ),
)
