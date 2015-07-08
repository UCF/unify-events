import logging
import time
import sys

import bleach
import HTMLParser
from bs4 import BeautifulSoup

from django.conf import settings
from django.core.management.base import BaseCommand

from events.models import Event

class Command(BaseCommand):
    count = 0

    def handle(self, *args, **options):
        self.clean_data()

    def custom_clean(self, value):
        """
        Custom function that uses Bleach and BeautifulSoup to remove
        unwanted markup and contents.
        Uses settings from the django-bleach module.
        """
        if value:
            # not None or empty string

            # Replace newline instances with linebreaks. Remove carriage returns.
            value = value.replace('\n', '<br />')
            value = value.replace('\r', '')

            # Convert brackets so BeautifulSoup can parse django-cleaned stuff.
            # Even if it's an escaped <script> tag, we want to get rid of it.
            value = value.replace('&lt;', '<')
            value = value.replace('&gt;', '>')

            soup = BeautifulSoup(value)
            all_tags = soup.findAll(True)
            for tag in all_tags:
                if tag.name in settings.BANNED_TAGS:
                    tag.extract()

            value = bleach.clean(soup)
        return value

    def remove_html(value):
        """
        Run Bleach on the given value because UNL Events doesn't do HTML sanitization on anything.

        Bleach here does NOT use the configuration settings in settings.py--it will remove
        ALL tags and attributes found.
        """
        if value:
            value = bleach.clean(value, tags=[], attributes={}, styles=[], strip=True)
            h = HTMLParser.HTMLParser()
            value = h.unescape(value)
        return value

    def update_progress(self, idx):
        progress = idx / self.count * 100
        sys.stdout.write('\r[{0}] {1}% {2}/{3}'.format('#'*(progress/10), progress, idx, self.count))
        sys.stdout.flush()

    def clean_data(self):
        events = Event.objects.all()
        self.count = len(events)
        for idx, event in enumerate(events):
            event.title = self.remove_html(event.title)
            event.description = self.custom_clean(event.description)
            try:
                event.save()
            except Exception, e:
                print e.message
                print 'Title: ', event.title
                print 'Decsription: ', event.description
            self.update_progress(idx)