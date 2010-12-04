from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('events.views',
	# http://events.ucf.edu/athletics/
	# http://events.ucf.edu/athletics/2010
	# http://events.ucf.edu/athletics/2010/01
	# http://events.ucf.edu/athletics/2010/01/10
	url(r'^(?P<calendar>[\w-]+)(\.(?P<format>[\w]+))?$',
		view='event_list',
		name="event-list"
	),
	url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)(\.(?P<format>[\w]+))?$',
		view='event_list',
		name="year-event-list"
	),
	url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)(\.(?P<format>[\w]+))?$',
		view='event_list',
		name="month-event-list"
	),
	url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)(\.(?P<format>[\w]+))?$',
		view='event_list',
		name="day-event-list"
	),
	
	# http://events.ucf.edu/athletics/this-year
	# http://events.ucf.edu/athletics/today
	# etc.
	url(r'^(?P<calendar>[\w-]+)/(?P<type>[\w-]+)(\.(?P<format>[\w]+))?$',
		view='named_event_list',
		name="named-event-list"
	),
)