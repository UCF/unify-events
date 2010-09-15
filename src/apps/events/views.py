MODULE = __import__(__name__)

from django.http                 import HttpResponse404
from django.views.generic.simple import direct_to_template
from models                      import *

# Create your views here.
def event_listing(request, calendar, type, format="html"):
	"""Outputs a listing of events defined by a calendar and type of
	listing.  Different formats of event lists can be outputted by specifying
	the optional format argument.
	"""
	#Convert calendar slug to id
	if calendar.isdigit(): calendar = int(calendar)
	else: calendar = Calendar.objects.get_object_or_404(slug=calendar)
	
	#Get view
	func = getattr(MODULE, type + '_events', None)
	if func is not None:
		return func(request, calendar, format)
	else:
		return HttpResponse404()


def todays_events(request, calendar, format):
	return direct_to_template(request, template, data)
	

def years_events(request, calendar, format):
	return direct_to_template(request, template, data)


def months_events(request, calendar, format):
	return direct_to_template(request, template, data)


def upcoming_events(request, calendar, format):
	return direct_to_template(request, template, data)