from django.db import models

import random

class PromotionManager(models.Manager):
    def single_random(self):
        """
        Returns the first or a random promotion based on
        the kwargs passed into the function.
        """
        if self.count() == 0:
            return None
        idx = random.randrange(0, self.count())
        objects = self.get_queryset().filter(active=True)
        return objects[idx]


class Promotion(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(null=False, blank=False)
    alt_text = models.CharField(max_length=500, null=False, blank=False)
    url = models.URLField(null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PromotionManager()

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title
