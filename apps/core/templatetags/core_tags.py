from dateutil import parser
import urllib

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
def include_esi(context, model, object_id, template_name, calendar_id=None, params=None):
    if settings.DEV_MODE:
        response = esi(context['request'], model, str(object_id), template_name, str(calendar_id), params)
        return response.content
    else:
        if calendar_id is not None:
            url = '/esi/' + model + '/' + str(object_id) + '/calendar/' + str(calendar_id) + '/' + template_name + '/'
        else:
            url = '/esi/' + model + '/' + str(object_id) + '/' + template_name + '/'

        if params:
            url = url + '?' + params
        # Keep the single quotes around src='' so that it doesn't mess
        # up ESIs that are used for HTML classes
        # Example: <div class="pull-left <esi:include src='/esi/category/1/slug/' />"></div>
        return "<esi:include src='%s' />" % url


@register.filter
def parse_date(value):
    if isinstance(value, basestring):
        value = parser.parse(value)
    return value


@register.filter
def quote_plus(value):
    return urllib.quote_plus(value.encode('utf-8'))