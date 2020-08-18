from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import SplitDateTimeWidget, DateInput, TimeInput
from django.forms.utils import to_current_timezone
from django.utils.safestring import mark_safe

import datetime

class Wysiwyg(forms.Textarea):
    def use_required_attribute(self, initial):
        return False

class TaggitField(forms.TextInput):
    def use_required_attribute(self, initial):
        return False

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

    def __init__(self, attrs=None, date_format=None, time_format=None, date_placeholder=None, time_placeholder=None):
        date_class = attrs.get('date_class')
        del attrs['date_class']

        time_class = attrs.get('time_class')
        del attrs['time_class']

        date_placeholder = attrs.get('date_placeholder')
        del attrs['date_placeholder']

        time_placeholder = attrs.get('time_placeholder')
        del attrs['time_placeholder']

        widgets = (DateInput(attrs={'class': date_class, 'placeholder': date_placeholder}, format=date_format),
                   TimeInput(attrs={'class': time_class, 'placeholder': time_placeholder}, format=time_format))
        super(SplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        values = super(BootstrapSplitDateTimeWidget, self).value_from_datadict(data, files, name)
        value = "{0} {1}".format(values[0], values[1])

        try:
            return datetime.datetime.strptime(value, '%m/%d/%Y %I:%M %p')
        except:
            return None
