from django import template
from seo.models import AutoAnchor

register = template.Library()

@register.filter(name='auto_anchors')
def auto_anchors(value, arg=None):
    patterns = AutoAnchor.objects.find_in_text(value)
    for pattern in patterns:
        value = value.replace(pattern.pattern,
            f'<a href="{pattern.url}" target="_blank">{pattern.pattern}</a>', 1)

    return value
