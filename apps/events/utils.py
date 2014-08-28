import logging

from clearcache import clearcache
from django.conf import settings

import events.models

log = logging.getLogger(__name__)


def event_ban_urls(sender, instance, **kwargs):
    """
    Bans urls for the event
    """
    urls = []

    for event_instance in instance.event_instances.all():
        urls.append('/event/' + str(event_instance.pk) +'/')
    urls.append('/calendar/'+ str(instance.calendar.pk) +'/')
    urls.append('/category/'+ str(instance.category.pk) +'/')
    for tag in instance.tags.all():
        urls.append('/tag/'+ str(instance.calendar.pk) +'/')

    cal = instance.calendar
    if instance.calendar.is_main_calendar:
        urls.extend(get_main_cal_bans())

    ban_urls(urls)


def generic_ban_urls(sender, instance, **kwargs):
    """
    Bans urls for a calendar
    """
    urls = []

    urls.append('/' + instance.__class__.__name__.lower() + '/' + str(instance.pk) + '/')

    if isinstance(instance, events.models.Calendar) and instance.is_main_calendar:
        urls.extend(get_main_cal_bans())

    ban_urls(urls)


def get_main_cal_bans():
    """
    Creates a list of main calendar bans.
    """
    return ['/', '/this-(week|month|year)/', '/upcoming/', '/week-of/', '/[0-9]{4}/']


def ban_urls(url_list):
    """
    Bans a list of urls.
    """
    if settings.ENABLE_CLEARCACHE:
        url_list.append('/search/')
        url_combo_list = [s + '.*' for s in url_list]
        cacheCleaner = clearcache.CacheHandler(settings.ALLOWED_HOSTS, settings.VARNISH_NODES)
        cacheCleaner.ban_url_list(url_combo_list)
    else:
        return

