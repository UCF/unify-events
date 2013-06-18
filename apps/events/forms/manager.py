from django import forms
from django.contrib.auth.models import User
from events.forms.fields import InlineLDAPSearchField
from events.modelers import Calendar
from profiles.models import Profile


class CalendarForm(forms.ModelForm):

    class Meta:
        model = Calendar
        fields = ('name', )


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', )


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('display_name', )


class EventCopyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        calendars = kwargs.pop('calendars')
        super(EventCopyForm, self).__init__(*args, **kwargs)
        self.fields['calendars'].queryset = calendars

    calendars = forms.ModelMultipleChoiceField(queryset=Calendar.objects.none(),label='Calendars to copy to:')