from django.db import models
from django.utils import timezone

from datetime import datetime

from events.models import Event

# Create your models here.
class InternalLinkManager(models.Manager):
    def find_in_text(self, text: str):
        link_ids = []

        for link in self.all():
            if any([phrase.phrase.lower() in text.lower() for phrase in link.phrases.all()]):
                link_ids.append(link.id)

        return self.filter(id__in=link_ids)

class InternalLink(models.Model):
    url = models.URLField(max_length=255, null=False, blank=False)
    created_on = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    updated_on = models.DateTimeField(null=False, blank=False, auto_now=True)
    imported = models.BooleanField(default=False)
    objects = InternalLinkManager()

    @property
    def keywords(self) -> str:
        return ', '.join(self.phrases.values_list('phrase', flat=True))

    def local(self) -> bool:
        return not self.imported
    local.boolean = True

    def __str__(self):
        return self.url

class KeywordPhrase(models.Model):
    phrase = models.CharField(max_length=255, null=False, blank=False)
    link = models.ForeignKey(InternalLink, related_name='phrases', on_delete=models.CASCADE)

    def __str__(self):
        return self.phrase

class InternalLinkRecord(models.Model):
    internal_link = models.ForeignKey(InternalLink, related_name='replacement_records', on_delete=models.CASCADE)
    keyword_phrase = models.ForeignKey(KeywordPhrase, related_name='replacements', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='internal_link_replacements', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(null=False, blank=False, auto_now=True)

    def __str__(self):
        return f"{self.keyword_phrase.phrase} - {self.internal_link.url}"
