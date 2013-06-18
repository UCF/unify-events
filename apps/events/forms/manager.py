from django import forms

from events.models import Calendar, Event


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
    description = forms.CharField(widget=forms.Textarea())
    calendar = forms.ModelChoiceField(queryset=Calendar.objects.none())

    class Meta:
        model = Event
        fields = ('title', 'description', 'calendar')


class EventCopyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        calendars = kwargs.pop('calendars')
        super(EventCopyForm, self).__init__(*args, **kwargs)
        self.fields['calendars'].queryset = calendars

    calendars = forms.ModelMultipleChoiceField(queryset=Calendar.objects.none(),label='Calendars to copy to:')