from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('events.views',
	# http://events.ucf.edu/calendar/athletics/event/20404/football-ucf-at-fsu
	# http://events.ucf.edu/calendar/athletics/event/20404/football-ucf-at-fsu.rss
	url(r'^(?P<calendar>[\w-]+)/event/(?P<instance_id>[\d]+)(/[\w-]+)?(\.(?P<format>[\w]+))?$',
		view='event_instance',
		name='event-instance'
	),
	
	# http://events.ucf.edu/calendar/athletics
	# http://events.ucf.edu/calendar/athletics/2010.json
	# http://events.ucf.edu/calendar/athletics/2010/01
	# http://events.ucf.edu/calendar/athletics/2010/01/10.rss
	url(r'^(?P<calendar>[\w-]+)(\.(?P<format>[\w]+))?$',
		view='calendar',
		name="calendar"
	),
	url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)(\.(?P<format>[\w]+))?$',
		view='auto_event_list',
		name="year-event-list"
	),
	url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)(\.(?P<format>[\w]+))?$',
		view='auto_event_list',
		name="month-event-list"
	),
	url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)(\.(?P<format>[\w]+))?$',
		view='auto_event_list',
		name="day-event-list"
	),
	
	# http://events.ucf.edu/calendar/athletics/from/2010-01-02/to/2010-02-02
	url(r'^(?P<calendar>[\w-]+)/from/(?P<start>[\w-]+)/to/(?P<end>[\w-]+)(\.(?P<format>[\w]+))?$',
		view='range_event_list',
		name="range-event-list"
	),
	
	
	# http://events.ucf.edu/calendar/athletics/this-year
	# http://events.ucf.edu/calendar/athletics/today
	# etc.
	url(r'^(?P<calendar>[\w-]+)/(?P<type>[\w-]+)(\.(?P<format>[\w]+))?$',
		view='named_event_list',
		name="named-event-list"
	),
)