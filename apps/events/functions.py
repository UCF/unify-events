def sluggify(original):
    """Apps sluggyify logic, to be used wherever slugs need to be generated."""
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
    dates = list()

    # Create date and event mapping
    for event in events:
        day = date(*(event.start.year, event.start.month, event.start.day))

        if day not in dates:
            dates.append(day)
            date_event_map[day] = list()

        date_event_map[day].append(event)

    return (dates, date_event_map)


def chunk(i, c_size):
    """Split an interable into even sized chunks defined by c_size.  If the
    number of items in the iterable cannot be evenly divided by c_size, the
    remainder will fall into the final element."""
    import math
    chunks = int(math.ceil(len(i) / float(c_size)))
    return [i[c * c_size : c * c_size + c_size] for c in range(0, chunks)]


def format_to_mimetype(format):
    """Provides a mapping between frontend document formats and mimetypes to be
    returned with the resulting response.
    """
    return {
        'json' : 'application/json',
        'rss'  : 'application/rss+xml',
        'html' : 'text/html',
        'xml'  : 'text/xml',
        'ics'  : 'text/calendar',
    }.get(format, 'text/html')