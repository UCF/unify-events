def sluggify(original):
	"""docstring for sluggify"""
	import re
	slug  = original.lower().strip()
	slug  = re.sub("[\s]+", '-', slug)
	slug  = re.sub("[^a-z1-9\s\-]", '', slug)
	return slug


def get_date_event_map(events):
	"""Get a tuple containing a list of dates and a mapping between those dates
	and the events that occur on them."""
	from datetime import date
	date_event_map = dict()
	dates          = list()
	
	# Create date and event mapping
	for event in events:
		day = date(*(event.start.year, event.start.month, event.start.day))
		
		if day not in dates:
			dates.append(day)
			date_event_map[day] = list()
		
		date_event_map[day].append(event)
	
	return (dates, date_event_map)