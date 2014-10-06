from django.db.models.fields import FieldDoesNotExist
from django.template.defaultfilters import slugify

import events.models


def generate_unique_slug(title, clazz, unique):
    """
    Generate a unique slug for the given class
    """
    slug = slugify(title)

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


def pre_save_strip_strings(sender, **kwargs):
    """
    Check all fields passed by the sender for strings and
    strip whitespace at the start and end of string before saving.
    """
    instance = kwargs['instance']
    for fieldname in instance._meta.get_all_field_names():
        try:
            # get_field_by_name returns (field_object, model, direct, m2m)
            field = instance._meta.get_field_by_name(fieldname)
            field = field[0]
            try:
                # Only update directly-accessible strings
                val = getattr(instance, fieldname)
                if isinstance(val, basestring):
                    setattr(instance, fieldname, val.strip())
            except (ValueError, AttributeError):
                # Pass when trying to get fields that we cannot access, e.g.
                # Taggit in particular will not allow you to access the
                # tags attr on an event before the event finishes saving.
                pass
        except FieldDoesNotExist:
            # Probably a foreign key, just pass
            pass


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