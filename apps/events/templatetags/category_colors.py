from django import template
from django.template import Context
from django.template import loader

from events.models import Category

register = template.Library()


@register.simple_tag(takes_context=True)
def category_color_styles(context):
    context = {
        'categories': Category.objects.all(),
        'request': context['request']
    }

    template = loader.get_template('events/widgets/category-color-styles.html')

    html = template.render(Context(context))

    return html