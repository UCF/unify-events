from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('events.views',
	# http://events.ucf.edu/athletics/
	# http://events.ucf.edu/athletics/2010
	# http://events.ucf.edu/athletics/2010/01
	# http://events.ucf.edu/athletics/2010/01/10
	url(r'^/$', 'event_list'),
	url(r'^/(?P<year>[\d]+)/$', 'event_list'),
	url(r'^/(?P<year>[\d]+)/(?P<month>[\d]+)/$', 'event_list'),
	url(r'^/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/$', 'event_list'),
	
	# http://events.ucf.edu/athletics/this-year
	# http://events.ucf.edu/athletics/today
	# etc.
	url(r'^/(?P<type>[\w-]+)/$', 'special_event_list'),
)