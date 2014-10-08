from django.db import models
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.db.models.signals import post_delete

from core.models import TimeCreatedModified
from core.utils import pre_save_slug
from core.utils import pre_save_strip_strings
from events.utils import generic_ban_urls


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
        ordering = ['title']

    def __str__(self):
        return self.title

    def __unicode__(self):
        return unicode(self.title)

pre_save.connect(pre_save_slug, sender=Category)
pre_save.connect(pre_save_strip_strings, sender=Category)
post_save.connect(generic_ban_urls, sender=Category)
post_delete.connect(generic_ban_urls, sender=Category)
