import urlparse
import re

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import post_delete

from core.models import TimeCreatedModified
from events.utils import generic_ban_urls


class Location(TimeCreatedModified):
    """
    Location
    """
    title = models.CharField(max_length=256)
    url = models.URLField(max_length=400, blank=True, null=True)
    room = models.CharField(max_length=256, blank=True, null=True)
    reviewed = models.BooleanField(default=False)
    import_id = models.CharField(max_length=256, blank=True, null=True)

    @property
    def comboname(self):
        comboname = self.title
        if self.room:
            comboname += ': ' + self.room
        return comboname

    @property
    def get_map_widget_url(self):
        """
        Given an event location url, returns a UCF map widget url with proper
        parameters, if the url is a valid map.ucf.edu permalink.
        """
        maps_domain = settings.MAPS_DOMAIN
        widget_url = False
        widget_url_base = "//"+ maps_domain +"/widget?title=&width=607&height=300&illustrated=n&zoom=14&building_id="
        location_id = None
        if maps_domain in self.url:
            parsed_url = urlparse.urlparse(self.url)
            # Check for 'map.ucf.edu/?show=locationID'
            if maps_domain + "/?show=" in self.url:
                location_id = urlparse.parse_qs(parsed_url.query)['show'][0]
            # Check for 'map.ucf.edu/locations/locationID/...'
            elif maps_domain + "/locations/" in self.url:
                match = re.search('^/locations/([a-zA-Z0-9_-]+)/', parsed_url.path)
                if match:
                    location_id = match.group(1)

            if location_id:
                widget_url = widget_url_base + location_id

        return widget_url

    class Meta:
        app_label = 'events'

    def __repr__(self):
        return '<' + self.comboname + '>'

    def __str__(self):
        return self.comboname

    def __unicode__(self):
        return unicode(self.comboname)

post_save.connect(generic_ban_urls, sender=Location)
post_delete.connect(generic_ban_urls, sender=Location)
