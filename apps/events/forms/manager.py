from events.modelers import Calendar

from django import forms


class CalendarForm(forms.ModelForm):

    class Meta:
        model = Calendar
        fields = ('name', 'description', )


class EventCopyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        calendars = kwargs.pop('calendars')
        super(EventCopyForm, self).__init__(*args, **kwargs)
        self.fields['calendars'].queryset = calendars

    calendars = forms.ModelMultipleChoiceField(queryset=Calendar.objects.none(),label='Calendars to copy to:')