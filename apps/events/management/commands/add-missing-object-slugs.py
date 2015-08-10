import logging
import time
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from events.models import Calendar
from events.models import Category
from events.models import Event


"""
Use this script if objects in the events system exist with empty slug values.
"""


class Command(BaseCommand):
    count = 0

    def handle(self, *args, **options):
        self.clean_data()

    def update_progress(self, idx):
        percent = float(idx) / self.count
        hashes = '#' * int(round(percent * 20))
        spaces = ' ' * (20 - len(hashes))
        sys.stdout.write('\r[{0}] {1}% {2}/{3}'.format(hashes + spaces, int(round(percent * 100)), idx, self.count))
        sys.stdout.flush()

    def clean_data(self):
        from core.utils import generate_unique_slug

        calendars = Calendar.objects.filter(slug=u'')
        categories = Category.objects.filter(slug=u'')
        events = Event.objects.filter(slug=u'')

        self.count = len(calendars) + len(categories) + len(events)

        """
        These loops are intentially not DRY so that we can defer the import
        of generate_unique_slug to avoid circular dependency issues and not
        have to do the import within a separate function that repeats per
        modified object
        """
        if calendars:
            for idx, cal in enumerate(calendars):
                try:
                    cal.slug = generate_unique_slug(cal.title, Calendar, False)
                    cal.save()
                except Exception, e:
                    print e.message
                    print 'Title: ', cal.title
                    print 'Slug: ', cal.slug
                self.update_progress(idx)

        if categories:
            for idx, cat in enumerate(categories):
                try:
                    cat.slug = generate_unique_slug(cat.title, Category, False)
                    cat.save()
                except Exception, e:
                    print e.message
                    print 'Title: ', cat.title
                    print 'Slug: ', cat.slug
                self.update_progress(idx)

        if events:
            for idx, event in enumerate(events):
                try:
                    event.slug = generate_unique_slug(event.title, Event, False)
                    event.save()
                except Exception, e:
                    print e.message
                    print 'Title: ', event.title
                    print 'Slug: ', event.slug
                self.update_progress(idx)
