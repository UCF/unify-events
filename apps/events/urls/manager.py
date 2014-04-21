from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from events.models import State
from events.views.manager import Dashboard
from events.views.manager.calendar import CalendarCreate
from events.views.manager.calendar import CalendarDelete
from events.views.manager.calendar import CalendarUpdate
from events.views.manager.calendar import CalendarUserUpdate
from events.views.manager.calendar import CalendarSubscriptionsUpdate
from events.views.manager.calendar import CalendarList
from events.views.manager.category import CategoryCreate
from events.views.manager.category import CategoryUpdate
from events.views.manager.category import CategoryDelete
from events.views.manager.category import CategoryList
from events.views.manager.event import EventCreate
from events.views.manager.event import EventDelete
from events.views.manager.event import EventUpdate
from events.views.manager.location import LocationCreateView
from events.views.manager.location import LocationDeleteView
from events.views.manager.location import LocationListView
from events.views.manager.location import LocationUpdateView
from events.views.manager.tag import TagCreateView
from events.views.manager.tag import TagDeleteView
from events.views.manager.tag import TagListView
from events.views.manager.tag import TagUpdateView

if settings.SEARCH_ENABLED:
    from haystack.views import search_view_factory
    from events.views.manager.search import ManagerSearchView

urlpatterns = patterns('',
                       url(r'^login/$',
                           view='django.contrib.auth.views.login',
                           kwargs={'template_name': 'events/manager/login.html'},
                           name='accounts-login'),
                       url(r'^logout/$',
                           view='django.contrib.auth.views.logout',
                           kwargs={'template_name': 'events/manager/logout.html'},
                           name='accounts-logout')
                       )

urlpatterns += patterns('events.views.manager',

    url(r'^event/(?P<pk>\d+)/copy', view='event.copy', name='event-copy'),
    url(r'^event/(?P<pk>\d+)/update', login_required(EventUpdate.as_view()), name='event-update'),
    url(r'^event/(?P<pk>\d+)/submit-to-main', view='event.submit_to_main', name='event-submit-to-main'),
    url(r'^event/(?P<pk>\d+)/post', view='event.update_state', name='event-post', kwargs={'state':State.posted}),
    url(r'^event/(?P<pk>\d+)/pend', view='event.update_state', name='event-pend', kwargs={'state':State.pending}),
    url(r'^event/(?P<pk>\d+)/cancel', view='event.cancel_uncancel', name='event-cancel-uncancel'),
    url(r'^event/(?P<pk>\d+)/delete', login_required(EventDelete.as_view()), name='event-delete'),
    url(r'^event/create', login_required(EventCreate.as_view()), name='event-create'),
    url(r'^event/bulk-action/', view='event.bulk_action', name='event-bulk-action'),

    url(r'^calendar/create/?$',
        view=login_required(CalendarCreate.as_view()),
        name='calendar-create'
    ),
    url(r'^calendar/(?P<pk>\d+)/delete/?$',
        view=login_required(CalendarDelete.as_view()),
        name='calendar-delete'
    ),
    url(r'^calendar/(?P<pk>\d+)/update/?$',
        view=login_required(CalendarUpdate.as_view()),
        name='calendar-update'
    ),
    url(r'^calendar/(?P<pk>\d+)/update/users/?$',
        view=login_required(CalendarUserUpdate.as_view()),
        name='calendar-update-users'
    ),
    url(r'^calendar/(?P<pk>\d+)/update/subscriptions/?$',
        view=login_required(CalendarSubscriptionsUpdate.as_view()),
        name='calendar-update-subscriptions'
    ),
    url(r'^calendar/(?P<pk>\d+)/(?P<state>[\w]+)?$', login_required(Dashboard.as_view()), name='dashboard-calendar-state'),
    url(r'^calendar/(?P<pk>\d+)/update/user/(?P<username>[\w]+)/(?P<role>[\w]+)?$', view='calendar.add_update_user', name='calendar-add-update-user'),
    url(r'^calendar/(?P<pk>\d+)/delete/user/(?P<username>[\w]+)', view='calendar.delete_user', name='calendar-delete-user'),
    url(r'^calendar/(?P<pk>\d+)/reassign-ownership/user/(?P<username>[\w]+)', view='calendar.reassign_ownership', name='calendar-reassign-ownership'),
    url(r'^calendar/(?P<pk>\d+)/unsubscribe-from/(?P<subscribed_calendar_id>\d+)?$', view='calendar.unsubscribe_from_calendar', name='calendar-unsubscribe'),
    url(r'^calendar/(?P<subscribing_calendar_id>\d+)/subscribe-to/(?P<pk>\d+)?$', view='calendar.subscribe_to_calendar', name='calendar-subscribe'),
    url(r'^calendar/(?P<pk>\d+)/?$', login_required(Dashboard.as_view()), name='dashboard'),
    url(r'^calendar/(?P<pk>\d+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/?$',
        login_required(Dashboard.as_view()),
        name='manager-day-listing'
    ),
    url(r'^(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/?$',
        login_required(Dashboard.as_view()),
        name='manager-all-calendars-day-listing'
    ),
    url(r'^all-calendars/?$',
        view=login_required(CalendarList.as_view()),
        name='calendar-list'
    ),

    url(r'^location/?$', login_required(LocationListView.as_view()), name='location-list'),
    url(r'^location/create/?$', login_required(LocationCreateView.as_view()), name='location-create'),
    url(r'^location/(?P<pk>\d+)/update', login_required(LocationUpdateView.as_view()), name='location-update'),
    url(r'^location/(?P<location_from_id>\d+)/merge/(?P<location_to_id>\d+)', view='location.merge', name='location-merge'),
    url(r'^location/(?P<pk>\d+)/delete', login_required(LocationDeleteView.as_view()), name='location-delete'),
    url(r'^location/(?P<state>[\w]+)?$', login_required(LocationListView.as_view()), name='location-state'),
    url(r'^location/bulk-action/', view='location.bulk_action', name='location-bulk-action'),

    url(r'^tag/?$', login_required(TagListView.as_view()), name='tag-list'),
    url(r'^tag/create/?$', login_required(TagCreateView.as_view()), name='tag-create'),
    url(r'^tag/(?P<pk>\d+)/update/?$', login_required(TagUpdateView.as_view()), name='tag-update'),
    url(r'^tag/(?P<tag_from_id>\d+)/merge/(?P<tag_to_id>\d+)', view='tag.merge', name='tag-merge'),
    url(r'^tag/(?P<pk>\d+)/delete', login_required(TagDeleteView.as_view()), name='tag-delete'),

    url(r'^category/create/?$',
        view=login_required(CategoryCreate.as_view()),
        name='category-create'
    ),
    url(r'^category/(?P<pk>\d+)/update/?$',
        view=login_required(CategoryUpdate.as_view()),
        name='category-update'
    ),
    url(r'^category/(?P<pk>\d+)/delete/?$',
        view=login_required(CategoryDelete.as_view()),
        name='category-delete'
    ),
    url(r'^category/?$',
        view=login_required(CategoryList.as_view()),
        name='category-list'
    ),
    url(r'^category/(?P<category_from_id>\d+)/merge/(?P<category_to_id>\d+)',
        view='category.merge',
        name='category-merge'
    ),

    url(r'^profiles/', include('profiles.urls')),

    #TODO do we need _date/?
    url(r'^date/(?P<_date>[\w-]+)/calendar/(?P<calendar_id>\d+)', login_required(Dashboard.as_view()), name='dashboard'),
    url(r'^date/(?P<_date>[\w-]+)/?$', login_required(Dashboard.as_view()), name='dashboard'),
    # ^^^^

    url(r'^$', login_required(Dashboard.as_view()), name='dashboard'),
    url(r'^state/(?P<state>[\w]+)?$', login_required(Dashboard.as_view()), name='dashboard-state'),
)

# Search-related URLs
if settings.SEARCH_ENABLED:
    urlpatterns += patterns('haystack.views',
        url(r'^search/$', login_required(search_view_factory(
            view_class=ManagerSearchView,
            template='search/manager-search.html'
        )), name='haystack_search_manager'),
    )
else:
    urlpatterns += patterns('events.views.manager',
        url(r'^search/$', login_required(Dashboard.as_view()), name='haystack_search_manager'),
    )
