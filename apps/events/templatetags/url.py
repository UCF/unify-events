import sys

from django import template
from django.conf import settings
from django.template.base import kwarg_re
from django.template.defaulttags import URLNode
from django.utils.encoding import smart_text
from django.utils import six
from django.utils.encoding import force_text
from django.utils.html import conditional_escape

register = template.Library()


class EventsURLNode(URLNode):
    """
    Custom URLNode class that checks for special url names and
    adjusts those values as necessary (i.e. for Main Calendar views.)
    """
    def render(self, context):
        from django.urls import reverse, NoReverseMatch
        args = [arg.resolve(context) for arg in self.args]
        kwargs = {
            force_text(k, 'ascii'): v.resolve(context)
            for k, v in self.kwargs.items()
        }
        view_name = self.view_name.resolve(context)
        try:
            current_app = context.request.current_app
        except AttributeError:
            try:
                current_app = context.request.resolver_match.namespace
            except AttributeError:
                current_app = None

        # Catch Main Calendar views and override url name
        calendar_urls = ['calendar', 'day-listing', 'week-listing', 'month-listing', 'year-listing', 'named-listing']
        if view_name in calendar_urls:
            calendar_pk = kwargs['pk']
            if calendar_pk == settings.FRONT_PAGE_CALENDAR_PK:
                if view_name == 'calendar':
                    view_name = 'home'
                else:
                    view_name = 'main-calendar-%s' % view_name

        # Try to look up the URL twice: once given the view name, and again
        # relative to what we guess is the "main" app. If they both fail,
        # re-raise the NoReverseMatch unless we're using the
        # {% url ... as var %} construct in which case return nothing.
        url = ''
        try:
            url = reverse(view_name, args=args, kwargs=kwargs, current_app=current_app)
        except NoReverseMatch:
            exc_info = sys.exc_info()
            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = reverse(project_name + '.' + view_name,
                              args=args, kwargs=kwargs, current_app=current_app)
                except NoReverseMatch:
                    if self.asvar is None:
                        # Re-raise the original exception, not the one with
                        # the path relative to the project. This makes a
                        # better error message.
                        six.reraise(*exc_info)
            else:
                if self.asvar is None:
                    raise

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            if context.autoescape:
                url = conditional_escape(url)
            return url

@register.tag(name='url')
def url(parser, token):
    """
    Overrides Django's built-in url template tag to accomodate for custom
    url patterns (i.e. for Main Calendar views.)

    Code is copied directly from django.template.defaulttags url function
    but replaces the return value.
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument, the name of a url()." % bits[0])
    viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return EventsURLNode(viewname, args, kwargs, asvar)
