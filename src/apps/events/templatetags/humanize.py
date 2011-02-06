from django import template

register = template.Library()

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