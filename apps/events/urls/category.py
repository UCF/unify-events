from django.conf.urls import url

from events.views.event_views import EventsByCategoryList


urlpatterns = [
    # https://events.ucf.edu/category/category-name
    url(r'^(?P<category_pk>\d+)/(?P<category>[\w-]+)/(?:feed\.(?P<format>[\w]+))?$',
        view=EventsByCategoryList.as_view(),
        name='events.views.category.category'
    ),
]
