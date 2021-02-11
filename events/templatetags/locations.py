from django import template

register = template.Library()

@register.filter
def locations_comboname(d, key):
    return d.get(pk=key).comboname

@register.filter
def locations_title(d, key):
    return d.get(pk=key).title

@register.filter
def locations_room(d, key):
    return d.get(pk=key).room or ''

@register.filter
def locations_url(d, key):
    return d.get(pk=key).url
