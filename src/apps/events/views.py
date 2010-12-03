MODULE = __import__(__name__)

from django.http                 import HttpResponseNotFound
from django.views.generic.simple import direct_to_template
from models                      import *

# http://events.ucf.edu/athletics/today
# http://events.ucf.edu/athletics/this-month
# http://events.ucf.edu/athletics/this-year
# http://events.ucf.edu/athletics/2010/01/10
# http://events.ucf.edu/athletics/2010/01/10?format=rss|ical|_html_|json

# Create your views here.
def event_list(request, calendar, year=None, month=None, day=None):
	"""Outputs a listing of events defined by a calendar and type of
	listing.  Different formats of event lists can be outputted by specifying
	the optional format argument.
	"""
	print calendar, year, month, day
	
	return HttpResponseNotFound()
	
	calendar = Calendar.objects.get_object_or_404(slug=calendar)
	
	
	


def special_event_list(request, calendar, type):
	f = {
		'today'      : todays_event_list,
		'this-month' : months_event_list,
		'this-year'  : years_event_list,
	}.get(type, None)
	if f is not None:
		return f(request, calendar)
	return HttpResponseNotFound()


from time import gmtime
YEAR, MONTH, DAY = 0, 1, 2

def todays_event_list(request, calendar):
	now = gmtime()
	year, month, day = now[YEAR], now[MONTH], now[DAY]
	return event_list(request, calendar, year, month, day)
	

def years_event_list(request, calendar):
	now = gmtime()
	year, month, day = now[YEAR], None, None
	return event_list(request, calendar, year, month, day)


def months_event_list(request, calendar):
	now = gmtime()
	year, month, day = now[YEAR], now[MONTH], None
	return event_list(request, calendar, year, month, day)
