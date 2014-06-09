import urlparse
import re

from django.db import models

from core.models import TimeCreatedModified


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
        widget_url = False
        widget_url_base = "//map.ucf.edu/widget?title=&width=607&height=300&illustrated=n&zoom=14&building_id="
        location_id = None
        if "map.ucf.edu" in self.url:
            parsed_url = urlparse.urlparse(self.url)
            # Check for 'map.ucf.edu/?show=locationID'
            if "map.ucf.edu/?show=" in self.url:
                location_id = urlparse.parse_qs(parsed_url.query)['show'][0]
            # Check for 'map.ucf.edu/locations/locationID/...'
            elif "map.ucf.edu/locations/" in self.url:
                match = re.search('^/locations/([a-z0-9]+)/', parsed_url.path)
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
