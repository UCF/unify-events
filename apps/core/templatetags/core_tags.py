from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def include_esi_template(context, template):
    """
    Return ESI code if not in DEBUG mode.
    """
    if settings.DEBUG:
        return render_to_string(template, context)
    else:
        return '<esi:include src="%s" />' % reverse('esi-template', args=(template,))
