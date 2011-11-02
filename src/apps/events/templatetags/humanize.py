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
	template   = loader.get_template('events/calendar/parts/event-list.html')
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
def pretty_date(d, format = ''):
	from django.template.defaultfilters import date
	from datetime                       import datetime, timedelta
	
	now    = datetime.now()
	today  = now.date()
	tomorrow = today + timedelta(days=1)
	diff   = d - now
	d_date = d.date()
	
	past_two_days    = lambda: d < now and diff.days >= 2
	past_one_day     = lambda: d < now and d_date == today - timedelta(days=1)
	past_today       = lambda: d < now and d_date == today
	future_two_weeks = lambda: d > now and diff.days >= 14
	future_one_week  = lambda: d > now and diff.days >= 7
	future_two_days  = lambda: d > now and diff.days >= 2
	future_one_day   = lambda: d > now and d_date == today + timedelta(days=1)
	future_today     = lambda: d > now and d_date == today
	
	
	tests = (
		past_two_days,
		past_one_day,
		past_today,
		future_two_weeks,
		future_one_week,
		future_two_days,
		future_one_day,
		future_today,
	)
	
	formats = {
		'frontend' : {
			'default'        : lambda: "starts at " + date(d, "ga"),
			past_two_days    : lambda: "started " + date(d, "F j, Y"),
			past_one_day     : lambda: "started yesterday",
			past_today       : lambda: "started at " + date(d, "ga"),
			future_two_weeks : lambda: date(d, "F j, Y"),
			future_one_week  : lambda: "next week, " + date(d, "F j"),
			future_two_days  : lambda: date(d, "l, ga"),
			future_one_day   : lambda: "Tomorrow, " + date(d, "ga"),
		},
		'manager' : {
			'default'        : lambda: date(d, "g a"),
			past_two_days    : lambda: date(d, "F j, Y g a"),
			past_one_day     : lambda: "Yesterday, " + date(d, "g a"),
			past_today       : lambda: date(d, "g a"),
			future_two_weeks : lambda: date(d, "F j, Y g a"),
			future_one_week  : lambda: "Next " + date(d, "l, g a"),
			future_two_days  : lambda: date(d, "l, g a"),
			future_one_day   : lambda: "Tomorrow, " + date(d, "g a"),
		},
		'calendar' : {
			'default'        : lambda: "Starts " + date(d, "F j, Y"),
			past_two_days    : lambda: "Started " + date(d, "F j, Y"),
			past_one_day     : lambda: "Started yesterday",
			past_today       : lambda: "Started at " + date(d, "ga"),
			future_one_week  : lambda: "Next " + date(d, "l, ga"),
			future_two_days  : lambda: date(d, "l, ga"),
			future_one_day   : lambda: "Starts tomorrow at " + date(d, "ga"),
			future_today     : lambda: "Starts at " + date(d, 'ga'),
		},
	}
	
	r = None
	format = formats.get(format, formats['frontend'])
	for test in tests:
		if test():
			r = format.get(test, format['default'])()
			break
	
	if not r:
		r = format['default']()
	
	return r.replace('.', '')


@register.filter('digit_to_word')
def digit_to_word(d):
	words = ['zero','one','two','three','four','five','six','seven','eight','nine']
	try:
		d = int(d)
	except ValueError:
		return 'unknown'
	else:
		return words[d] if d < 10 else d
