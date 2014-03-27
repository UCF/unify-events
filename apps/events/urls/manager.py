from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from events.models import State
from events.views.manager import Dashboard
from events.views.manager.event import EventCreate
from events.views.manager.event import EventUpdate
from events.views.manager.calendar import CalendarCreate
from events.views.manager.calendar import CalendarUpdate
from events.views.manager.calendar import CalendarDelete

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

    url(r'^search/user/(?P<firstname>\w+)?/?(?P<lastname>\w+)?/?$', view='search_user', name='search-user'),
    url(r'^search/event/?', view='search_event', name='search-event'),

    url(r'^event/(?P<pk>\d+)/copy', view='event.copy', name='event-copy'),
    url(r'^event/(?P<pk>\d+)/update', login_required(EventUpdate.as_view()), name='event-update'),
    url(r'^event/(?P<pk>\d+)/submit-to-main', view='event.submit_to_main', name='event-submit-to-main'),
    url(r'^event/(?P<pk>\d+)/post', view='event.update_state', name='event-post', kwargs={'state':State.posted}),
    url(r'^event/(?P<pk>\d+)/pend', view='event.update_state', name='event-pend', kwargs={'state':State.pending}),
    url(r'^event/(?P<pk>\d+)/cancel', view='event.cancel_uncancel', name='event-cancel-uncancel'),
    url(r'^event/(?P<pk>\d+)/delete', view='event.delete', name='event-delete'),
    url(r'^event/create', login_required(EventCreate.as_view()), name='event-create'),
    url(r'^event/bulk-action/', view='event.bulk_action', name='event-bulk-action'),

    url(r'^calendar/create/?$',
        view=login_required(CalendarCreate.as_view()),
        name='calendar-create'
    ),
    url(r'^calendar/(?P<pk>\d+)/update/?$',
        view=login_required(CalendarUpdate.as_view()),
        name='calendar-update'
    ),
    url(r'^calendar/(?P<pk>\d+)/delete/?$',
        view=login_required(CalendarDelete.as_view()),
        name='calendar-delete'
    ),
    url(r'^calendar/(?P<calendar_id>\d+)/(?P<state>[\w]+)?$', login_required(Dashboard.as_view()), name='dashboard-calendar-state'),
    url(r'^calendar/(?P<calendar_id>\d+)/update/user/(?P<username>[\w]+)/(?P<role>[\w]+)?$', view='calendar.add_update_user', name='calendar-add-update-user'),
    url(r'^calendar/(?P<calendar_id>\d+)/delete/user/(?P<username>[\w]+)', view='calendar.delete_user', name='calendar-delete-user'),
    url(r'^calendar/(?P<calendar_id>\d+)/reassign-ownership/user/(?P<username>[\w]+)', view='calendar.reassign_ownership', name='calendar-reassign-ownership'),
    url(r'^calendar/(?P<calendar_id>\d+)/unsubscribe-from/(?P<subscribed_calendar_id>\d+)?$', view='calendar.unsubscribe_from_calendar', name='calendar-unsubscribe'),
    url(r'^calendar/(?P<subscribing_calendar_id>\d+)/subscribe-to/(?P<calendar_id>\d+)?$', view='calendar.subscribe_to_calendar', name='calendar-subscribe'),
    url(r'^calendar/(?P<calendar_id>\d+)/?$', login_required(Dashboard.as_view()), name='dashboard'),
    url(r'^calendar/(?P<calendar_id>\d+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(\.(?P<format>[\w]+))?$',
        login_required(Dashboard.as_view()),
        name='manager-day-listing'
    ),
    url(r'^(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(\.(?P<format>[\w]+))?$',
        login_required(Dashboard.as_view()),
        name='manager-all-calendars-day-listing'
    ),

    url(r'^location/?$', view='location.list', name='location-list'),
    url(r'^location/create/?$', view='location.create_update', name='location-create'),
    url(r'^location/(?P<location_id>\d+)/update', view='location.create_update', name='location-update'),
    url(r'^location/(?P<state>[\w]+)?$', view='location.list', name='location-state'),
    url(r'^location/bulk-action/', view='location.bulk_action', name='location-bulk-action'),

    url(r'^tag/?$', view='tag.list', name='tag-list'),
    url(r'^tag/create/?$', view='tag.create_update', name='tag-create'),
    url(r'^tag/(?P<tag_id>\d+)/update/?$', view='tag.create_update', name='tag-update'),
    url(r'^tag/(?P<tag_from_id>\d+)/merge/(?P<tag_to_id>\d+)', view='tag.merge', name='tag-merge'),
    url(r'^tag/(?P<tag_id>\d+)/delete', view='tag.delete', name='tag-delete'),

    url(r'^category/?$', view='category.list', name='category-list'),
    url(r'^category/create/?$', view='category.create_update', name='category-create'),
    url(r'^category/(?P<category_id>\d+)/update', view='category.create_update', name='category-update'),
    url(r'^category/(?P<category_from_id>\d+)/merge/(?P<category_to_id>\d+)', view='category.merge', name='category-merge'),
    url(r'^category/(?P<category_id>\d+)/delete', view='category.delete', name='category-delete'),

    url(r'^all-calendars/?$', view='calendar.list', name='calendar-list'),

    url(r'^profiles/', include('profiles.urls')),

    url(r'^date/(?P<_date>[\w-]+)/calendar/(?P<calendar_id>\d+)', login_required(Dashboard.as_view()), name='dashboard'),
    url(r'^date/(?P<_date>[\w-]+)/?$', login_required(Dashboard.as_view()), name='dashboard'),
    url(r'^$', login_required(Dashboard.as_view()), name='dashboard'),
    url(r'^state/(?P<state>[\w]+)?$', login_required(Dashboard.as_view()), name='dashboard-state'),
)
