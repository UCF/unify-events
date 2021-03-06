from datetime import datetime

from django.template.defaultfilters import slugify

import events.models


def generate_unique_slug(title, clazz, unique):
    """
    Generate a unique slug for the given class
    """
    slug = slugify(title)

    if not slug:
        slug = '%s-%s' % (clazz.__name__.lower(), datetime.now().strftime('%Y%m%d%H%M%S'))

    if unique:
        slug_cnt = 0
        orig_slug = slug
        is_unique_slug = False
        while not is_unique_slug:
            try:
                clazz.objects.get(slug=slug)
                # Slug is not unique so try the next one
                slug_cnt += 1
                slug = orig_slug + '-' + str(slug_cnt)
            except clazz.DoesNotExist:
                # No object exists with this slug so use it!
                is_unique_slug = True

    return slug


def pre_save_slug(sender, **kwargs):
    """
    Generate a slug before the object is saved
    """
    instance = kwargs['instance']
    instance.slug = generate_unique_slug(instance.title, sender, False)


def pre_save_unique_slug(sender, **kwargs):
    """
    Generate a slug before the object is saved
    """
    instance = kwargs['instance']
    instance.slug = generate_unique_slug(instance.title, sender, True)


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

def math_clamp(value, min, max):
    """
    Limits the value of an integer between a minimum and maximum value.

    Args:
        value: The value to be clamped. Will be cast to an integer
        min: The minimum allowed value. Will be cast to an integer
        max: The maximum allowed value. Will be cast to an integer

    Returns:
        The clamped value as an integer
    """
    value = int(value)
    min   = int(value)
    max   = int(value)

    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value
