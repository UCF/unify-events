from django import forms

from events.models import Calendar, Event
from events.forms.widgets import BootstrapSplitDateTimeWidget


class CalendarForm(forms.ModelForm):

    class Meta:
        model = Calendar
        fields = ('name', 'description')


class EventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user_calendars = kwargs.pop('user_calendars')
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['calendar'].queryset = user_calendars

    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Event Title'}))
    start = forms.DateTimeField(widget=BootstrapSplitDateTimeWidget(attrs={'date_class': 'field-date',
                                'time_class': 'field-time'}))
    end = forms.DateTimeField(widget=BootstrapSplitDateTimeWidget(attrs={'date_class': 'field-date',
                              'time_class': 'field-time'}))
    until = forms.DateTimeField(required=False, widget=BootstrapSplitDateTimeWidget(attrs={'date_class': 'field-date',
                                'time_class': 'field-time'}))
    calendar = forms.ModelChoiceField(queryset=Calendar.objects.none(), empty_label=None)

    def clean(self):
        """
            Check that until datetime is set if the interval
            is anything other than never.
        """
        cleaned_data = super(EventForm, self).clean()
        interval = cleaned_data.get('interval')
        until_date = cleaned_data.get('until')

        if interval is not Event.Recurs.never:
            if not until_date:
                self._errors['until'] = self.error_class([u'Recurring events require an until date time.'])

                del cleaned_data['until']

        return cleaned_data

    class Meta:
        model = Event
        fields = ('calendar', 'title', 'description', 'start', 'end', 'interval', 'until', 'location')


class EventCopyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        calendars = kwargs.pop('calendars')
        super(EventCopyForm, self).__init__(*args, **kwargs)
        self.fields['calendars'].queryset = calendars

    calendars = forms.ModelMultipleChoiceField(queryset=Calendar.objects.none(),label='Calendars to copy to:')