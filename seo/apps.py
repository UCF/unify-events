from django.apps import AppConfig
from django.db.models.signals import pre_save

from seo.signals import pre_save_internal_link

class SeoConfig(AppConfig):
    name = 'seo'

    def ready(self) -> None:
        pre_save.connect(pre_save_internal_link, sender='seo.InternalLink')
        return super().ready()
