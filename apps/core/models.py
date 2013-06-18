from django.db import models
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