from django.db import models
from django.db.models.signals import class_prepared
from django.contrib.contenttypes.models import ContentType


class TimeCreatedModified(models.Model):
    """
    Base model to be used my most models. Includes a
    modified and created date.
    """
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class ContentTypeMixin(object):
    @property
    def model_content_type(self):
        return ContentType.objects.get(app_label=self._meta.app_label, model=self._meta.object_name)


def longer_first_last(sender, *args, **kwargs):
    """
    Change the max length of the first and last name
    """
    if sender.__name__ == 'User' and sender.__module__ == 'django.contrib.auth.models':
        sender._meta.get_field('first_name').max_length = 75
        sender._meta.get_field('last_name').max_length = 75

class_prepared.connect(longer_first_last)
