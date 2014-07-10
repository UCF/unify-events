from django import template
from django.conf import settings
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from core.views import esi

register = template.Library()


@register.simple_tag(takes_context=True)
def include_esi_template(context, template, params='', kwargs=None):
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


@register.simple_tag(takes_context=True)
def include_esi(context, model, object_id, template_name):
    url = 'esi/' + model + '/' + str(object_id) + template_name + '/'
    if settings.DEV_MODE:
        response = esi(context['request'], model, str(object_id), template_name)
        return response.content
    else:
        return '<exi:include src="%s" />' % url
