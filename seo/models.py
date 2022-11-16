from django.db import models

# Create your models here.
class AutoAnchorManager(models.Manager):
    def find_in_text(self, text: str):
        pattern_ids = []

        for aa in self.all():
            if aa.pattern.lower() in text.lower():
                pattern_ids.append(aa.id)

        return self.filter(id__in=pattern_ids)

class AutoAnchor(models.Model):
    pattern = models.CharField(max_length=255, null=False, blank=False)
    url = models.URLField(max_length=255, null=False, blank=False)
    imported = models.BooleanField(default=False)
    created_on = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    updated_on = models.DateTimeField(null=False, blank=False, auto_now=True)
    objects = AutoAnchorManager()

    def local(self) -> bool:
        return not self.imported
    local.boolean = True

    def __str__(self):
        return self.pattern
