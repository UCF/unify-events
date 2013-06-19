from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.forms.widgets import SplitDateTimeWidget, DateInput, TimeInput
from django.forms.util import to_current_timezone


class InlineLDAPSearch(forms.Widget):

    def render(self, name, value, attrs=None):

        html = list()
        html.append('<div class="inlineldapsearch clearfix">')
        html.append('<div class="input"><input type="text" class="query" />')
        html.append('<button class="search">Search</button></div>')
        html.append('<select multiple="multiple" class="choices" size="5"></select>')
        html.append('<ul class="actions"><li><a class="add">Add</a></li>')
        html.append('<li><a class="remove">Remove</a></li></ul>')
        html.append('<select multiple="multiple" class="selections" name="%s">' % name)
        if value is not None:
            for user_id in value:
                user = User.objects.get(pk=user_id)
                display = user.first_name + ' ' + user.last_name + ' (' + user.username + ')'
                html.append('<option value="%d">%s</option>' % (user_id, display))
        html.append('</select></div>')
        return mark_safe(u'\n'.join(html))


class BootstrapSplitDateTimeWidget(SplitDateTimeWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """

    def __init__(self, attrs=None, date_format=None, time_format=None):
        date_class = attrs.get('date_class')
        del attrs['date_class']

        time_class = attrs.get('time_class')
        del attrs['time_class']

        widgets = (DateInput(attrs={'class': date_class}, format=date_format),
                   TimeInput(attrs={'class': time_class}, format=time_format))
        super(SplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]