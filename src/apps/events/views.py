MODULE = __import__(__name__)

from django.http                 import Http404, HttpResponse
from django.template             import TemplateDoesNotExist
from datetime                    import datetime, timedelta
from django.shortcuts            import get_object_or_404
from django.views.generic.simple import direct_to_template
from models                      import *

# http://events.ucf.edu/athletics/today
# http://events.ucf.edu/athletics/this-month
# http://events.ucf.edu/athletics/this-year
# http://events.ucf.edu/athletics/2010/
# http://events.ucf.edu/athletics/2010/01/
# http://events.ucf.edu/athletics/2010/01/10.(rss|json|html|xml|etc)

# Create your views here.
def calendar(request, calendar, format=None):
	calendar   = get_object_or_404(Calendar, slug=calendar)
	now        = gmtime()
	start      = datetime(now.tm_year, now.tm_mon, now.tm_mday)
	end        = start + timedelta(days=1)
	
	todays_events   = calendar.find_event_instances(start, end)
	featured_events = calendar.find_event_instances(start, end + timedelta(weeks=52), calendar.featured_instances)
	
	
	template = 'events/calendar.' + (format or 'html')
	context  = {
		'calendar'        : calendar,
		'todays_events'   : todays_events,
		'featured_events' : featured_events,
	}
	
	try:
		return direct_to_template(request, template, context)
	except TemplateDoesNotExist:
		raise Http404


def event_instance(request, calendar, instance_id, format=None):
	calendar = get_object_or_404(Calendar, slug=calendar)
	try:
		instance = calendar.events_and_subs.get(pk=instance_id)
	except EventInstance.DoesNotExist:
		raise Http404
	
	template = 'events/instance.' + (format or 'html')
	context  = {
		'calendar' : calendar,
		'instance' : instance,
	}
	
	try:
		return direct_to_template(request, template, context)
	except TemplateDoesNotExist:
		raise Http404


def event_list(request, calendar, start, end, format=None):
	"""Outputs a listing of events defined by a calendar and a range of dates.
	Format of this list is controlled by the optional format argument, ie. html,
	rss, json, etc.
	"""
	calendar = get_object_or_404(Calendar, slug=calendar)
	events   = calendar.find_event_instances(start, end)
	events   = events.order_by('start')
	template = 'events/list.' + (format or 'html')
	context  = {
		'start'    : start,
		'end'      : end,
		'format'   : format,
		'calendar' : calendar,
		'events'   : events,
	}
	try:
		return direct_to_template(request, template, context)
	except TemplateDoesNotExist:
		raise Http404


def auto_event_list(request, calendar, year=None, month=None, day=None, format=None):
	"""Generates an event listing for the defined, year, month, day, or today."""
	# Default if no date is defined
	if year is month is day is None:
		return todays_event_list(request, calendar)
	
	try: # Convert applicable arguments to integer
		year  = int(year) if year is not None else year
		month = int(month) if month is not None else month
		day   = int(day) if day is not None else day
	except ValueError:
		raise Http404
	
	# Define start and end dates
	try:
		start = datetime(year, month or 1, day or 1)
		
		if month is None:
			end = datetime(year + 1, 1, 1)
		elif day is None:
			roll = month > 11 #Check for December to January rollover
			end  = datetime(
				year + 1 if roll else year,
				month + 1 if not roll else 1,
				1
			)
		else:
			end = start + timedelta(days=1)
	except ValueError:
		raise Http404
	
	return event_list(request, calendar, start, end, format)


from time import gmtime, time
ONE_DAY = 86400

def named_event_list(request, calendar, type, format=None):
	"""Handles named event listings, such as today, this-month, or this-year."""
	f = {
		'today'      : todays_event_list,
		'tomorrow'   : tomorrows_event_list,
		'this-month' : months_event_list,
		'this-week'  : weeks_event_list,
		'this-year'  : years_event_list,
	}.get(type, None)
	if f is not None:
		return f(request, calendar, format)
	raise Http404


def range_event_list(request, calendar, start, end, format=None):
	from datetime import datetime
	date  = lambda d: datetime(*[int(i) for i in d.split('-')])
	start = date(start)
	end   = date(end)
	return event_list(request, calendar, start, end, format)


def todays_event_list(request, calendar, format=None):
	"""Generates event listing for the current day"""
	now = gmtime()
	year, month, day = now.tm_year, now.tm_mon, now.tm_mday
	return auto_event_list(request, calendar, year, month, day, format)


def tomorrows_event_list(request, calendar, format=None):
	"""Generates event listing for the current day"""
	now = gmtime(time() + ONE_DAY)
	year, month, day = now.tm_year, now.tm_mon, now.tm_mday
	return auto_event_list(request, calendar, year, month, day, format)


def weeks_event_list(request, calendar, format=None):
	"""Generates event listing for the current week"""
	today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	start = today - timedelta(days=today.weekday())
	end   = start + timedelta(weeks=1)
	return event_list(request, calendar, start, end, format)


def months_event_list(request, calendar, format=None):
	"""Generates event listing for the current month"""
	now = gmtime()
	year, month, day = now.tm_year, now.tm_mon, None
	return auto_event_list(request, calendar, year, month, day, format)


def years_event_list(request, calendar, format=None):
	"""Generates event listing for the current year"""
	now = gmtime()
	year, month, day = now.tm_year, None, None
	return auto_event_list(request, calendar, year, month, day, format)

