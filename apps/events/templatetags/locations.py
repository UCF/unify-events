from django import template
register = template.Library()

@register.filter
def locations_comboname(d, key):
    return d.get(pk=key).comboname

@register.filter
def locations_name(d, key):
    return d.get(pk=key).name

@register.filter
def locations_room(d, key):
    return d.get(pk=key).room

@register.filter
def locations_url(d, key):
    return d.get(pk=key).url