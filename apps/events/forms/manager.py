from django import forms
from django.contrib.auth.models import User

from events.models import Calendar
from events.models import Event
from events.models import EventInstance
from events.forms.fields import InlineLDAPSearchField
from events.forms.widgets import BootstrapSplitDateTimeWidget


class CalendarForm(forms.ModelForm):
    """
    For for the Calendar
    """
    editors = InlineLDAPSearchField(queryset=User.objects.none(), required=False)
    
    class Meta:
        model = Calendar
        fields = ('name', 'description', 'editors')


class EventForm(forms.ModelForm):
    """
    Form for an Event
    """
    def __init__(self, *args, **kwargs):
        user_calendars = kwargs.pop('user_calendars')
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['calendar'].queryset = user_calendars

        instance = kwargs['instance']
        if instance and instance.created_from:
            if instance.created_from.title is instance.title:
                self.fields['new_title'] = forms.CharField(required=False, initial=instance.title)
                self.fields['new_title'].widget.attrs['disabled'] = 'disabled'

            if instance.created_from.description is instance.description:
                self.fields['new_description'] = forms.CharField(required=False,
                                                                 initial=instance.description,
                                                                 widget=forms.Textarea(attrs={'disabled': 'disabled'}))

        self.fields['submit_to_main'] = forms.BooleanField(required=False)
        if instance and instance.is_submit_to_main:
            self.fields['submit_to_main'].widget.attrs['disabled'] = 'disabled'
            self.fields['submit_to_main'].initial = True

    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Event Title'}))
    calendar = forms.ModelChoiceField(queryset=Calendar.objects.none(), empty_label=None)

    class Meta:
        model = Event
        fields = ('calendar', 'title', 'description', 'contact_name', 'contact_email', 'contact_phone')


class EventInstanceForm(forms.ModelForm):
    """
    Form for the EventInstance
    """
    start = forms.DateTimeField(widget=BootstrapSplitDateTimeWidget(attrs={'date_class': 'field-date',
                                               'time_class': 'field-time'}))
    end = forms.DateTimeField(widget=BootstrapSplitDateTimeWidget(attrs={'date_class': 'field-date',
                                             'time_class': 'field-time'}))
    until = forms.DateField(required=False)

    class Meta:
        model = EventInstance
        fields = ('start', 'end', 'interval', 'until', 'location')
    

class EventCopyForm(forms.Form):
    """
    Copy event to a specified calendar
    """
    def __init__(self, *args, **kwargs):
        calendars = kwargs.pop('calendars')
        super(EventCopyForm, self).__init__(*args, **kwargs)
        self.fields['calendars'].queryset = calendars

    calendars = forms.ModelMultipleChoiceField(queryset=Calendar.objects.none(), label='Calendars to copy to:')