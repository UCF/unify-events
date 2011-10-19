from django.conf.urls.defaults import *
from events.models             import Event
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
	url(r'^search/event/?', view='search_event', name='search-event'),

	url(r'^event/(?P<id>\d+)/copy', view='event.copy', name='event-copy'),
	url(r'^event/(?P<id>\d+)/update', view='event.create_update', name='event-update'),
	url(r'^event/(?P<id>\d+)/post', view='event.update_state', name='event-post', kwargs={'state':Event.Status.posted}),
	url(r'^event/(?P<id>\d+)/pend', view='event.update_state', name='event-pend', kwargs={'state':Event.Status.pending}),
	url(r'^event/(?P<id>\d+)/delete', view='event.delete', name='event-delete'),
	url(r'^event/create', view='event.create_update', name='event-create'),

	url(r'^tag/merge/from/(?P<from_id>\d+)/to/(?P<to_id>\d+)/?$', view='tag.create_update', name='tag-update'),
	url(r'^tag/(?P<id>\d+)/update/?$', view='tag.create_update', name='tag-update'),
	url(r'^tag/(?P<id>\d+)/delete/?$', view='tag.delete', name='tag-delete'),
	url(r'^tag/create/?$', view='tag.create_update', name='tag-create'),
	url(r'^tag/manage/?$', view='tag.manage', name='tag-manage'),

	url(r'^category/merge/from/(?P<from_id>\d+)/to/(?P<to_id>\d+)/?$', view='category.create_update', name='category-update'),
	url(r'^category/(?P<id>\d+)/update/?$', view='category.create_update', name='category-update'),
	url(r'^category/(?P<id>\d+)/delete/?$', view='category.delete', name='category-delete'),
	url(r'^category/create/?$', view='category.create_update', name='category-create'),
	url(r'^category/manage/?$', view='category.manage', name='category-manage'),

	url(r'^calendar/(?P<id>\d+)/update/?$', view='calendar.create_update', name='calendar-update'),
	url(r'^calendar/(?P<id>\d+)/delete/?$', view='calendar.delete', name='calendar-delete'),
	url(r'^calendar/create/?$', view='calendar.create_update', name='calendar-create'),

	url(r'^accounts/profile', view='accounts.profile', name='accounts-profile'),
	
	url(r'^category/(?P<category_name>.+)/?', view='dashboard', name='dashboard-category'),
	url(r'^tag/(?P<tag_name>.+)/?', view='dashboard', name='dashboard-tag'),
	url(r'^date/(?P<_date>[\w-]+)/calendar/(?P<calendar_id>\d+)', view='dashboard', name='dashboard'),
	url(r'^date/(?P<_date>[\w-]+)/?$', view='dashboard', name='dashboard'),
	url(r'^calendar/(?P<calendar_id>\d+)/?$', view='dashboard', name='dashboard'),
	url(r'^$', view='dashboard', name='dashboard'),
)