from django.db import models
from django.db.models.signals import pre_save

from core.models import TimeCreatedModified
from core.utils import pre_save_slug


class Category(TimeCreatedModified):
    """
    Used to cateogorize objects
    """
    title = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, blank=True)
    color = models.CharField(max_length=60, blank=True)

    class Meta:
        app_label = 'events'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title

    def __unicode__(self):
        return unicode(self.title)

pre_save.connect(pre_save_slug, sender=Category)
