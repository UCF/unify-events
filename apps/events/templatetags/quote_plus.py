import urllib

from django import template

register = template.Library()


@register.filter
def quote_plus(value):
    return urllib.quote_plus(value)