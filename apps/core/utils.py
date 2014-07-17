from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify

import events.models


def create_redirect(sender, instance):
    """
    Generates redirect rules for objects whose slugs have changed on update
    """
    models_with_slug_urls = ['Calendar', 'Event', 'Category', 'Tag']
    if sender._meta.object_name in models_with_slug_urls:
        try:
            o = sender.objects.get(pk=instance.pk)
            if o.slug != instance.slug:
                old_path = o.get_absolute_url()
                new_path = instance.get_absolute_url()
                # Update any existing redirects that are pointing to the old url
                for redirect in Redirect.objects.filter(new_path=old_path):
                    redirect.new_path = new_path
                    # If the updated redirect now points to itself, delete it
                    # (i.e. slug = A -> slug = B -> slug = A again)
                    if redirect.new_path == redirect.old_path:
                        redirect.delete()
                    else:
                        redirect.save()
                # Now add the new redirect
                Redirect.objects.create(
                    site=Site.objects.get_current(),
                    old_path=old_path,
                    new_path=new_path)
        except sender.DoesNotExist:
            pass


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

    create_redirect(sender, instance)


def pre_save_unique_slug(sender, **kwargs):
    """
    Generate a slug before the object is saved
    """
    instance = kwargs['instance']
    instance.slug = generate_unique_slug(instance.title, sender, True)

    create_redirect(sender, instance)


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