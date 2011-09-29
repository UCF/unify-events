from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('events.views.calendar',
	# http://events.ucf.edu/calendar/athletics/event/20404/football-ucf-at-fsu
	# http://events.ucf.edu/calendar/athletics/event/20404/football-ucf-at-fsu.rss
	url(r'^(?P<calendar>[\w-]+)/event/(?P<instance_id>[\d]+)(/[\w-]+)?(\.(?P<format>[\w]+))?$',
		view='event',
		name='event'
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
		view='auto_listing',
		name="year-listing"
	),
	url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)(\.(?P<format>[\w]+))?$',
		view='auto_listing',
		name="month-listing"
	),
	url(r'^(?P<calendar>[\w-]+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)(\.(?P<format>[\w]+))?$',
		view='auto_listing',
		name="day-listing"
	),
	
	# http://events.ucf.edu/calendar/athletics/from/2010-01-02/to/2010-02-02
	url(r'^(?P<calendar>[\w-]+)/from/(?P<start>[\w-]+)/to/(?P<end>[\w-]+)(\.(?P<format>[\w]+))?$',
		view='range_listing',
		name="range-listing"
	),
	
	
	# http://events.ucf.edu/calendar/athletics/this-year
	# http://events.ucf.edu/calendar/athletics/today
	# etc.
	url(r'^(?P<calendar>[\w-]+)/(?P<type>[\w-]+)(\.(?P<format>[\w]+))?$',
		view='named_listing',
		name="named-listing"
	),
)