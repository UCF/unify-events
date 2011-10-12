from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('',
	url(r'^login/$', 
		view='django.contrib.auth.views.login',
		kwargs={'template_name':'events/manager/login.html'},
		name='accounts-login'),
	url(r'^logout/$',
		view='django.contrib.auth.views.logout',
		kwargs={'template_name':'events/manager/logout.html'},
		name='accounts-logout')
)

urlpatterns += patterns('events.views.manager',
	
	url(r'^search/user/(?P<lastname>\w+)?/?(?P<firstname>\w+)?/?$', view='search_user', name='search-user'),

	url(r'^event/(?P<id>\d+)/update', view='event.create_update', name='event-update'),
	url(r'^event/create', view='event.create_update', name='event-create'),
	
	url(r'^calendar/(?P<id>\d+)/update/?$', view='calendar.create_update', name='calendar-update'),
	url(r'^calendar/create/?$', view='calendar.create_update', name='calendar-create'),

	url(r'^accounts/profile', view='accounts.profile', name='accounts-profile'),
	
	url(r'^date/(?P<_date>[\w-]+)/calendar/(?P<calendar_id>\d+)', view='manage', name='manager'),
	url(r'^date/(?P<_date>[\w-]+)/?$', view='manage', name='manager'),
	url(r'^calendar/(?P<calendar_id>\d+)/?$', view='manage', name='manager'),
	url(r'^$', view='manage', name='manager'),
)