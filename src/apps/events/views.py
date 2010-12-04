MODULE = __import__(__name__)

from django.http                 import HttpResponseNotFound, HttpResponse
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
def event_list(request, calendar, start, end, format="html"):
	"""Outputs a listing of events defined by a calendar and a range of dates.
	Format of this list is controlled by the optional format argument, ie. html,
	rss, json, etc.
	"""
	calendar = get_object_or_404(Calendar, slug=calendar)
	events   = calendar.find_event_instances(start, end)
	
	template = 'events/list.' + format
	context  = {
		'start'    : start,
		'end'      : end,
		'year'     : year,
		'month'    : month,
		'day'      : day,
		'format'   : format,
		'calendar' : calendar,
		'events'   : events,
	}
	return direct_to_template(request, template, context)


def auto_event_list(request, calendar, year=None, month=None, day=None, format=None):
	"""Generates an event listing for the defined, year, month, day, or today."""
	start, end = None, None
	
	# Default if no date is defined
	if year is month is day is None:
		return today_event_list(request, calendar)
	
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
		return HttpResponseNotFound()
	
	return event_list(request, calendar, start, end, format)


from time import gmtime, time
YEAR    = 0
MONTH   = 1
DAY     = 2
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
	return HttpResponseNotFound()


def todays_event_list(request, calendar, format=None):
	"""Generates event listing for the current day"""
	now = gmtime()
	year, month, day = now[YEAR], now[MONTH], now[DAY]
	return auto_event_list(request, calendar, year, month, day, format)


def tomorrows_event_list(request, calendar, format=None):
	"""Generates event listing for the current day"""
	now = gmtime(time() + ONE_DAY)
	year, month, day = now[YEAR], now[MONTH], now[DAY]
	return auto_event_list(request, calendar, year, month, day, format)


def weeks_event_list(request, calendar, format=None):
	"""Generates event listing for the current week"""
	start = datetime.now()
	end   = start + timedelta(weeks=1)
	return event_list(request, calendar, start, end, format)


def months_event_list(request, calendar, format=None):
	"""Generates event listing for the current month"""
	now = gmtime()
	year, month, day = now[YEAR], now[MONTH], None
	return auto_event_list(request, calendar, year, month, day, format)


def years_event_list(request, calendar, format=None):
	"""Generates event listing for the current year"""
	now = gmtime()
	year, month, day = now[YEAR], None, None
	return auto_event_list(request, calendar, year, month, day, format)

