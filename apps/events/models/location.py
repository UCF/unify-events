from django.db import models

from core.models import TimeCreatedModified


class Location(TimeCreatedModified):
    """
    Location
    """
    title = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    room = models.CharField(max_length=256, blank=True, null=True)
    reviewed = models.BooleanField(default=False)

    @property
    def comboname(self):
        comboname = self.title
        if self.room:
            comboname += ': ' + self.room
        return comboname

    class Meta:
        app_label = 'events'

    def __repr__(self):
        return '<' + self.comboname + '>'

    def __str__(self):
        return self.comboname

    def __unicode__(self):
        return unicode(self.comboname)