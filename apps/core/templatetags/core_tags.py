from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def include_esi_template(context, template, params=''):
    """
    Return ESI code if not in Development mode.
    """
    if settings.DEV_MODE:
        return render_to_string(template, context)
    else:
        if params:
            url = reverse('esi-template', args=(template,)) + '?' + params
        else:
            url = reverse('esi-template', args=(template,))

        return '<esi:include src="%s" />' % url
