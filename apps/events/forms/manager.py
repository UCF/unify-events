from django import forms
from django.contrib.auth.models import User
from events.forms.fields import InlineLDAPSearchField
from events.modelers import Calendar
from profiles.models import Profile


class CalendarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CalendarForm, self).__init__(*args, **kwargs)

        # Exclude calendar being edited from subscription list
        try:
            kwargs['instance']
        except KeyError:
            pass

    # subscriptions = forms.ModelMultipleChoiceField(queryset=Calendar.objects.filter(shared=True),required=False)
    # editors = forms.ModelMultipleChoiceField(queryset=User.objects.all())
    # editors = InlineLDAPSearchField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Calendar
        fields = ('name', 'slug')


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


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