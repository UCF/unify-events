from django.conf.urls import include, patterns, url

from events.models import Status

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

    url(r'^search/user/(?P<lastname>\w+)?/?(?P<firstname>\w+)?/?$', view='search_user', name='search-user'),
    url(r'^search/event/?', view='search_event', name='search-event'),

    url(r'^event/(?P<id>\d+)/copy', view='event.copy', name='event-copy'),
    url(r'^event/(?P<id>\d+)/update', view='event.create_update', name='event-update'),
    url(r'^event/(?P<id>\d+)/post', view='event.update_state', name='event-post', kwargs={'state':Status.posted}),
    url(r'^event/(?P<id>\d+)/pend', view='event.update_state', name='event-pend', kwargs={'state':Status.pending}),
    url(r'^event/(?P<id>\d+)/delete', view='event.delete', name='event-delete'),
    url(r'^event/create', view='event.create_update', name='event-create'),

    url(r'^calendar/(?P<id>\d+)/update/?$', view='calendar.create_update', name='calendar-update'),
    url(r'^calendar/(?P<id>\d+)/delete/?$', view='calendar.delete', name='calendar-delete'),
    url(r'^calendar/create/?$', view='calendar.create_update', name='calendar-create'),

    url(r'^profiles/', include('profiles.urls')),

    url(r'^date/(?P<_date>[\w-]+)/calendar/(?P<calendar_id>\d+)', view='dashboard', name='dashboard'),
    url(r'^date/(?P<_date>[\w-]+)/?$', view='dashboard', name='dashboard'),
    url(r'^calendar/(?P<calendar_id>\d+)/?$', view='dashboard', name='dashboard'),
    url(r'^$', view='dashboard', name='dashboard'),
)