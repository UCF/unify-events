import logging
import time
import sys

import bleach
from bleach.css_sanitizer import CSSSanitizer
from bs4 import BeautifulSoup

from django.conf import settings
from django.core.management.base import BaseCommand

from events.models import Event
from events.functions import remove_html


"""
Use this script if data imported from the UNL events system
(via import-unl-events.py) was dirty (event titles,
descriptions contained unfiltered markup).
"""


class Command(BaseCommand):
    count = 0

    bleach_args = {}
    # Mirrors django_bleach.utils.get_bleach_default_options(). bleach 5.0
    # replaced the `styles` argument with a CSSSanitizer instance.
    possible_settings = {
        'BLEACH_ALLOWED_TAGS': 'tags',
        'BLEACH_ALLOWED_ATTRIBUTES': 'attributes',
        'BLEACH_ALLOWED_STYLES': 'css_sanitizer',
        'BLEACH_STRIP_TAGS': 'strip',
        'BLEACH_STRIP_COMMENTS': 'strip_comments',
    }

    for setting, kwarg in possible_settings.items():
        if hasattr(settings, setting):
            value = getattr(settings, setting)
            if setting == 'BLEACH_ALLOWED_STYLES':
                value = CSSSanitizer(allowed_css_properties=value)
            bleach_args[kwarg] = value

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

            # Replace newline instances with linebreaks. Remove carriage
            # returns.
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

            # bleach.clean() rejects anything that is not a str.
            value = bleach.clean(str(soup), **self.bleach_args)
        return value

    def update_progress(self, idx):
        percent = float(idx) / self.count
        hashes = '#' * int(round(percent * 20))
        spaces = ' ' * (20 - len(hashes))
        sys.stdout.write('\r[{0}] {1}% {2}/{3}'.format(hashes + spaces, int(round(percent * 100)), idx, self.count))
        sys.stdout.flush()

    def clean_data(self):
        events = Event.objects.all()
        self.count = len(events)
        for idx, event in enumerate(events):
            event.title = remove_html(event.title)
            event.description = self.custom_clean(event.description)
            try:
                event.save()
            except Exception as e:
                print(e.message)
                print('Title: ', event.title)
                print('Decsription: ', event.description)
            self.update_progress(idx)
