from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

from events.models import State

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

    url(r'^event/(?P<event_id>\d+)/copy', view='event.copy', name='event-copy'),
    url(r'^event/(?P<event_id>\d+)/update', view='event.create_update', name='event-update'),
    url(r'^event/(?P<event_id>\d+)/submit-to-main', view='event.submit_to_main', name='event-submit-to-main'),
    url(r'^event/(?P<event_id>\d+)/post', view='event.update_state', name='event-post', kwargs={'state':State.posted}),
    url(r'^event/(?P<event_id>\d+)/pend', view='event.update_state', name='event-pend', kwargs={'state':State.pending}),
    url(r'^event/(?P<event_id>\d+)/delete', view='event.delete', name='event-delete'),
    url(r'^event/create', view='event.create_update', name='event-create'),
    url(r'^event/bulk-action/', view='event.bulk_action', name='event-bulk-action'),

    url(r'^calendar/create/?$', view='calendar.create_update', name='calendar-create'),
    url(r'^calendar/(?P<calendar_id>\d+)/update/?$', view='calendar.create_update', name='calendar-update'),
    url(r'^calendar/(?P<calendar_id>\d+)/delete/?$', view='calendar.delete', name='calendar-delete'),
    url(r'^calendar/(?P<calendar_id>\d+)/update/user/(?P<username>[\w]+)/(?P<role>[\w]+)?$', view='calendar.add_update_user', name='calendar-add-update-user'),
    url(r'^calendar/(?P<calendar_id>\d+)/delete/user/(?P<username>[\w]+)', view='calendar.delete_user', name='calendar-delete-user'),
    url(r'^calendar/(?P<calendar_id>\d+)/reassign-ownership/user/(?P<username>[\w]+)', view='calendar.reassign_ownership', name='calendar-reassign-ownership'),
    url(r'^calendar/(?P<calendar_id>\d+)/unsubscribe-from/(?P<subscribed_calendar_id>\d+)?$', view='calendar.unsubscribe_from_calendar', name='calendar-unsubscribe'),
    url(r'^calendar/(?P<subscribing_calendar_id>\d+)/subscribe-to/(?P<calendar_id>\d+)?$', view='calendar.subscribe_to_calendar', name='calendar-subscribe'),
    url(r'^calendar/(?P<calendar_id>\d+)/?$', view='dashboard', name='dashboard'),
    url(r'^calendar/(?P<calendar_id>\d+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(\.(?P<format>[\w]+))?$',
        view='dashboard',
        name='manager-day-listing'
    ),
    url(r'^(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/(\.(?P<format>[\w]+))?$',
        view='dashboard',
        name='manager-all-calendars-day-listing'
    ),

    url(r'^location/?$', view='location.list', name='location-list'),
    url(r'^location/create/?$', view='location.create_update', name='location-create'),
    url(r'^location/(?P<location_id>\d+)/update', view='location.create_update', name='location-update'),

    url(r'^profiles/', include('profiles.urls')),

    url(r'^date/(?P<_date>[\w-]+)/calendar/(?P<calendar_id>\d+)', view='dashboard', name='dashboard'),
    url(r'^date/(?P<_date>[\w-]+)/?$', view='dashboard', name='dashboard'),
    url(r'^$', view='dashboard', name='dashboard'),
    url(r'^state/(?P<state>[\w]+)?$', view='dashboard', name='dashboard-state'),
)
