import re
import settings

from django import template
from seo.models import AutoAnchor

register = template.Library()

@register.filter(name='auto_anchors')
def auto_anchors(value, arg=None):
    print(value)

    patterns = AutoAnchor.objects.find_in_text(value)
    for pattern in patterns:
        # anchor_re = f'<a.*(.*{pattern.pattern}.*)<\/a>'
        anchor_re = '(<a[^>]*>)(?P<content>.*College of Sciences.*)(<\/a>)'
        match = re.search(anchor_re, value)

        if match and settings.SEO_AUTO_ANCHORS_FORCE_UPDATE:
            value = re.sub(
                '(<a.+>)(.*College of Sciences.*)(<\/a>)',
                f'<a href="{pattern.url}" target="_blank">{match.group("content")}</a>',
                value,
                1
            )
            # Don't do the replacement again if regex replace happened
            continue
        elif match and settings.SEO_AUTO_ANCHORS_FORCE_UPDATE == False:
            continue

        value = value.replace(pattern.pattern,
            f'<a href="{pattern.url}" target="_blank">{pattern.pattern}</a>', 1)

    return value
