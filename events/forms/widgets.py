from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import SplitDateTimeWidget, DateInput, TimeInput
from django.forms.utils import to_current_timezone
from django.urls import reverse
from django.utils.safestring import mark_safe

from taggit.forms import TagWidget

import datetime

class Wysiwyg(forms.Textarea):
    def use_required_attribute(self, initial):
        return False

class TaggitField(TagWidget):
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
        return mark_safe('\n'.join(html))


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


class Select2AjaxSelect(forms.Select):
    """
    A <select> that ships nothing but its current selection and lets select2
    fetch the rest of the options from an AJAX endpoint as the user types.

    Use this in place of forms.Select wherever the choices come from a table
    big enough that writing every row into the page is the wrong trade -- the
    featured event picker, for example, would otherwise render an <option> for
    every published event on the main calendar.

    The field keeps its full queryset, so validation still rejects anything
    outside it. Only the rendering is narrowed.
    """

    def __init__(self, ajax_url_name, placeholder=None, minimum_input_length=0,
                 attrs=None, choices=()):
        self.ajax_url_name = ajax_url_name

        widget_attrs = {
            'data-select2-minimum-input': minimum_input_length,
        }
        if placeholder:
            widget_attrs['data-select2-placeholder'] = placeholder
        if attrs:
            widget_attrs.update(attrs)

        # ajaxSelect2Fields() finds these fields by class, so the hook has to
        # be merged in rather than assigned -- a caller passing classes of its
        # own through attrs would otherwise replace it and quietly leave the
        # field as a plain <select> holding a single option.
        classes = ['select2-ajax-select']
        classes += [
            css_class
            for css_class in str(widget_attrs.get('class', '')).split()
            if css_class != 'select2-ajax-select'
        ]
        widget_attrs['class'] = ' '.join(classes)

        super(Select2AjaxSelect, self).__init__(attrs=widget_attrs, choices=choices)

    def get_context(self, name, value, attrs):
        context = super(Select2AjaxSelect, self).get_context(name, value, attrs)
        # Resolved at render time rather than in __init__ so that importing the
        # form doesn't depend on the URLconf already being loaded.
        context['widget']['attrs']['data-select2-url'] = reverse(self.ajax_url_name)
        return context

    def optgroups(self, name, value, attrs=None):
        """
        Emit the empty option and the current selection, and nothing else.

        ChoiceWidget.optgroups walks self.choices, and for a ModelChoiceField
        that iterator is exactly what pulls every row out of the database and
        onto the page. Not walking it is the whole point of this widget.
        """
        options = []
        index = 0

        empty_label = getattr(self.field, 'empty_label', None)
        if empty_label is not None and not self.allow_multiple_selected:
            options.append(self.create_option(name, '', empty_label, False, index))
            index += 1

        for selected_value in value:
            if selected_value in ('', None):
                continue

            label = self.label_for_value(selected_value)
            if label is None:
                # The submitted value isn't in the queryset. Dropping it keeps
                # the markup honest; the field's own error explains why.
                continue

            options.append(self.create_option(name, selected_value, label, True, index))
            index += 1

        return [(None, options, 0)]

    @property
    def field(self):
        """
        The ModelChoiceField this widget belongs to, or None.

        ModelChoiceField._set_queryset hands the widget a ModelChoiceIterator,
        which carries a reference back to the field it came from.
        """
        return getattr(getattr(self, 'choices', None), 'field', None)

    def label_for_value(self, value):
        """
        Look up the label for a single already-selected value.

        This is one indexed lookup by primary key, in place of loading the
        whole queryset just to find the row that happens to be selected.
        """
        queryset = getattr(getattr(self, 'choices', None), 'queryset', None)
        if queryset is None:
            return None

        try:
            obj = queryset.filter(pk=value).first()
        except (ValueError, TypeError, ValidationError):
            # A malformed pk in the POST data -- not a match by definition.
            return None

        if obj is None:
            return None

        field = self.field
        if field is not None:
            return field.label_from_instance(obj)
        return str(obj)
