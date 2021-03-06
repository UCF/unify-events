import bleach
from bs4 import BeautifulSoup
from dateutil import parser
import html2text
import re
from unidecode import unidecode
from urllib.parse import quote_plus as urllib_quote_plus

from django import template
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import escapejs
from django.utils.safestring import mark_safe

from core.views import esi
from events.functions import remove_html
import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def include_esi_template(context, template, params='', kwargs=None):
    """
    Return ESI code if not in Development mode.
    """
    if settings.DEV_MODE:
        return render_to_string(template, context.flatten())
    else:
        if params:
            url = reverse('esi-template', args=(template,)) + '?' + params
        else:
            url = reverse('esi-template', args=(template,))

        return mark_safe('<esi:include src="%s" />' % url)


@register.simple_tag(takes_context=True)
def include_esi(context, model, object_id, template_name, calendar_id=None, params=None):
    if settings.DEV_MODE:
        response = esi(context['request'], model, str(object_id), template_name, str(calendar_id), params)
        content = mark_safe(response.content.decode(response.charset))
        return content
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
        return mark_safe("<esi:include src='%s' />" % url)


@register.simple_tag
def static_ver(path):
    """
    Appends a simple version stamp at the end of a given path.
    """
    url = settings.STATIC_URL + path

    try:
        separator = '?v='
        if '?' in path:
            separator = '&v='

        return url + separator + settings.APP_VERSION
    except AttributeError:
        # settings.APP_VERSION isn't defined
        return url


@register.simple_tag(takes_context=True)
def absolute_uri_query_transform(context, **kwargs):
    """
    Takes a request and generates an absolute URL with given
    kwargs as query parameters (updating existing param values
    if present).
    """
    request = context['request']
    updated = request.GET.copy()
    for k, v in list(kwargs.items()):
        updated[k] = v

    return request.build_absolute_uri('?' + updated.urlencode())


@register.filter
def parse_date(value):
    if isinstance(value, str):
        value = parser.parse(value)
    return value


@register.filter
def quote_plus(value):
    return urllib_quote_plus(value)

@register.filter(name='remove_html')
def custom_striptags(value):
    """
    Non-regex-based striptags replacement, using Bleach.
    """
    value = remove_html(value)
    return value

@register.filter
def bleach_linkify_noemail(value):
    return bleach.linkify(value, parse_email=False)


@register.filter
def escapeics(value):
    """
    Converts HTML markup to plaintext suitable for ICS format.
    """
    if value is None:
        value = ''

    # Converts non-ASCII content to ASCII
    value = unidecode(value)

    # Translates HTML to plain ASCII text (e.g. convert <br> to newlines)
    h2t = html2text.HTML2Text()
    h2t.body_width = 0
    h2t.ignore_emphasis = 1
    value = h2t.handle(value)

    # Remove ending newlines. ('\n' counts as ONE char)
    if value.endswith('\n'):
        value = value[:-1]

    # Make sure newlines are encoded properly.
    # http://stackoverflow.com/a/12249023
    value = value.replace('\n', '\\n')

    return mark_safe(value)


@register.filter
def escapexml(value):
    """
    Cleans xml text based on w3 standards http://www.w3.org/TR/REC-xml/

    Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]  /* any Unicode character, excluding the surrogate blocks, FFFE, and FFFF. */
    """
    if value is None:
        value = ''

    illegal_xml_chars_regex = re.compile(settings.ILLEGAL_XML_CHARS)
    value = illegal_xml_chars_regex.sub('', value)

    return value
