from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def include_esi_template(context, template, view_name='esi-template'):
    """
    Return ESI code if not in Development mode.
    """
    if settings.DEV_MODE:
        return render_to_string(template, context)
    else:
        return '<esi:include src="%s" />' % reverse(view_name, args=(template,))
