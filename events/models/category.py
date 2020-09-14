from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save

from core.models import TimeCreatedModified
from core.utils import pre_save_slug
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
        return str(self.title)

pre_save.connect(pre_save_slug, sender=Category)
post_save.connect(generic_ban_urls, sender=Category)
# using pre_delete because all the objects may not exist if done via
# post_delete (ex. event.calendar or event.tags if deleting a calendar)
# No harm done if the delete doesn't go through. Just causes a single
# miss on varnish.
pre_delete.connect(generic_ban_urls, sender=Category)
