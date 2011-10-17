from django                  import template
from django.template         import loader, Context
from django.utils.safestring import mark_safe
from django.conf             import settings

register = template.Library()

@register.simple_tag
def format_event_list(events, calendar):
	""" Return html with a list of events sectioned out by day they occur."""
	from datetime         import datetime
	from datetime         import datetime, date, timedelta
	from events.functions import get_date_event_map
	
	dates, date_event_map = get_date_event_map(events)
	
	# Initialize loop constants and containers
	date_lists = list()
	today      = date.today()
	template   = loader.get_template('events/calendar/event-list.html')
	prefix_gen = lambda d: {
		timedelta(1) : 'Tomorrow: ',
		timedelta(0) : 'Today: ',
	}.get(d - today, '')
	
	# Render lists for each date
	for date in dates:
		prefix   = prefix_gen(date)
		events   = date_event_map[date]
		heading  = prefix + date.strftime('%A, %B ') + str(date.day)
		date_lists.append(template.render(Context({
			'MEDIA_URL'   : settings.MEDIA_URL,
			'events'      : events,
			'heading'     : heading,
			'heading_tag' : 'h3',
			'calendar'    : calendar,
		})))
	
	# No events were provided, so we output empty results
	if not len(date_lists):
		date_lists.append(template.render(Context({
			'MEDIA_URL'   : settings.MEDIA_URL,
			'events'      : None,
			'heading'     : 'No events found',
			'heading_tag' : 'p',
			'calendar'    : calendar,
		})))
	
	# Combine lists and return joined list html
	html = '\n'.join(date_lists)
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


@register.filter('digit_to_word')
def digit_to_word(d):
	WORDS = ['zero','one','two','three','four','five','six','seven','eight','nine']
	try:
		d = int(d)
	except ValueError:
		return 'unknown'
	else:
		return WORDS[d] if d < 10 else d