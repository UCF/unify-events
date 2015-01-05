import bleach
from bs4 import BeautifulSoup
from dateutil import parser
import html2text
import urllib

from django import template
from django.conf import settings
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
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


@register.filter(name='remove_html')
def custom_striptags(value):
    """
    Non-regex-based striptags replacement, using Bleach.
    """
    value = remove_html(value)
    return value


bleach_args = {}
possible_settings = {
    'BLEACH_ALLOWED_TAGS': 'tags',
    'BLEACH_ALLOWED_ATTRIBUTES': 'attributes',
    'BLEACH_ALLOWED_STYLES': 'styles',
    'BLEACH_STRIP_TAGS': 'strip',
    'BLEACH_STRIP_COMMENTS': 'strip_comments',
}

for setting, kwarg in possible_settings.iteritems():
    if hasattr(settings, setting):
        bleach_args[kwarg] = getattr(settings, setting)



def custom_clean(value):
    """
    Custom function that uses Bleach and BeautifulSoup to remove
    unwanted markup and contents.
    Uses settings from the django-bleach module.
    """
    # Replace newline instances with linebreaks. Remove carriage returns.
    value = value.replace('\n', '<br />')
    value = value.replace('\r', '')

    # Convert brackets so BeautifulSoup can parse django-cleaned stuff.
    # Even if it's an escaped <script> tag, we want to get rid of it.
    value = value.replace('&lt;', '<')
    value = value.replace('&gt;', '>')

    soup = BeautifulSoup(value)
    all_tags = soup.findAll(True)
    for tag in all_tags:
        if tag.name in settings.BANNED_TAGS:
            tag.extract()

    value = bleach.clean(soup, **bleach_args)
    return value


@register.filter(name='custom_clean')
def custom_clean_safe(value):
    value = custom_clean(value)

    # Make sure we actually have something left to display
    if not value.strip():
        value = settings.FALLBACK_EVENT_DESCRIPTION

    return mark_safe(value)


@register.filter
def clean_and_linkify(value):
    """
    Removes unwanted HTML markup and contents and auto-generates link tags.
    """
    # Clean everything.
    stripped = custom_clean(value)

    # Linkify whatever is left
    new_value = bleach.linkify(stripped, parse_email=False)

    # Make sure we actually have something left to display
    if not new_value.strip():
        new_value = settings.FALLBACK_EVENT_DESCRIPTION

    return mark_safe(new_value)


@register.filter
def custom_clean_escapeics(value):
    """
    Converts HTML markup to plaintext suitable for ICS format.
    Runs custom_clean() to ensure content is safe.
    """
    # Clean the value
    value = custom_clean(value)

    # Convert to text.
    h2t = html2text.HTML2Text()
    h2t.body_width = 0
    value = h2t.handle(value)

    # Make sure newlines are encoded properly.
    # http://stackoverflow.com/a/12249023
    value = value.replace('\n', '\\n')

    # Make sure we actually have something left to display
    if not value.strip():
        value = settings.FALLBACK_EVENT_DESCRIPTION

    return mark_safe(value)


@register.filter
def custom_clean_escapejs(value):
    """
    Converts HTML markup to a string that is Javascript-safe.
    """
    # Clean the value
    value = custom_clean(value)

    # Escape value for js use
    value = escapejs(value)

    # Make sure we actually have something left to display
    if not value.strip():
        value = settings.FALLBACK_EVENT_DESCRIPTION

    return mark_safe(value)
