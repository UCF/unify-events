from django import template
from django.template import Context
from django.template import loader

from events.models import Category

register = template.Library()


@register.simple_tag
def category_color_styles():
    context = {
        'categories': Category.objects.all()
    }

    template = loader.get_template('events/widgets/category-color-styles.html')

    html = template.render(Context(context))

    return html