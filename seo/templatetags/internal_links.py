import re
import settings

from django import template
from seo.models import InternalLink

register = template.Library()

@register.filter(name='internal_links')
def internal_links(value, arg=None):
    links = InternalLink.objects.find_in_text(value)
    for link in links:
        phrases = '|'.join(link.phrases.values_list('phrase', flat=True))
        anchor_re = f'(<a[^>]*>)(?P<content>.*{phrases}.*)(<\/a>)'
        match = re.search(anchor_re, value)

        if match and settings.SEO_AUTO_ANCHORS_FORCE_UPDATE:
            value = re.sub(
                f'(<a[^>]*>)(?P<content>.*{phrases}.*)(<\/a>)',
                f'<a href="{link.url}" target="_blank">{match.group("content")}</a>',
                value,
                1
            )
            # Don't do the replacement again if regex replace happened
            continue
        elif match and settings.SEO_AUTO_ANCHORS_FORCE_UPDATE == False:
            continue

        for phrase in link.phrases.all():
            if phrase.phrase in value:
                value = value.replace(phrase.phrase,
                    f'<a href="{link.url}" target="_blank">{phrase.phrase}</a>', 1)
                break

    return value
