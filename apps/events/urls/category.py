from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls import url

from events.views.calendar import EventsByCategoryList


urlpatterns = patterns('events.views.category',
    # http://events.ucf.edu/category/category-name
    url(r'^(?P<category>[\w-]+)/(?P<format>[\w]+)?$',
        view=EventsByCategoryList.as_view(),
        name='category'
    ),
)
