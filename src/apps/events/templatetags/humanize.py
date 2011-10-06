from django                  import template
from django.template         import loader, Context
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter('format_event_list')
def format_event_list(events):
	""" Return html with a list of events sectioned out by day they occurr."""
	from datetime import datetime
	
	date_event_map = dict()
	dates          = list()
	
	for event in events:
		day = datetime(*(event.start.year, event.start.month, event.start.day))
		
		if day not in dates:
			dates.append(day)
			date_event_map[day] = list()
		
		date_event_map[day].append(event)
	
	lists = list()
	for date in dates:
		events   = date_event_map[date]
		heading  = date.strftime('%A, %B ') + str(date.day)
		template = loader.get_template('events/calendar/event-list.html')
		lists.append(template.render(Context({
			'events'      : events,
			'heading'     : heading,
			'heading_tag' : 'h3',
		})))
	
	html = '\n'.join(lists)
	return mark_safe(html)

@register.filter('pretty_date')
def pretty_date(d):
	from django.template.defaultfilters import date
	from datetime                       import datetime, timedelta
	now  = datetime.now()
	diff = d - now
	
	# diff is negative and greater than two days, started February 1, 2010
	if (diff < timedelta(0) and diff.days >= 2):
		return "started " + date(d, "F j, Y")
	# diff is negative and greater than one day, started yesterday
	if (diff < timedelta(0) and diff.days >= 1):
		return "started yesterday"
	# diff is negative, started at 9am
	if (diff < timedelta(0)):
		return "started at " + date(d, "g a")
	# diff is greater than two weeks, February 14, 2010
	if (diff.days >= 14):
		return date(d, "F j, Y")
	# diff is greater than one week, next week, February 7
	if (diff.days >= 7):
		return "next week, " + date(d, "F j")
	# diff is greater than two days, Friday, 2pm
	if (diff.days >= 2):
		return date(d, "l, g a")
	# diff is greater than one day, Tomorrow, 2pm
	if (diff.days >= 1):
		return "Tomorrow, " + date(d, "g a")
	# diff is less than one day, starts at 2pm
	return "starts at " + date(d, "g a")