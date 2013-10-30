from django import forms
from django.contrib.auth.models import User

from events.models import Calendar
from events.models import Event
from events.models import EventInstance
from events.models import Location
from events.forms.fields import InlineLDAPSearchField
from events.forms.widgets import BootstrapSplitDateTimeWidget


class CalendarForm(forms.ModelForm):
    """
    For for the Calendar
    """
    editors = InlineLDAPSearchField(queryset=User.objects.none(), required=False)

    class Meta:
        model = Calendar
        fields = ('title', 'description', 'editors')


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
        fields = ('calendar', 'title', 'description', 'contact_name', 'contact_email', 'contact_phone', 'category', 'tags')


class EventInstanceForm(forms.ModelForm):
    """
    Form for the EventInstance
    """
    start = forms.DateTimeField(widget=BootstrapSplitDateTimeWidget(attrs={'date_class': 'field-date',
                                               'time_class': 'field-time'}))
    end = forms.DateTimeField(widget=BootstrapSplitDateTimeWidget(attrs={'date_class': 'field-date',
                                             'time_class': 'field-time'}))
    until = forms.DateField(required=False)
    new_location_title = forms.CharField(required=False)
    new_location_room = forms.CharField(required=False)
    new_location_url = forms.URLField(required=False)

    def clean_new_location_url(self):
        """
        Ensure data is entered for new event instance locations
        """
        new_location_title = self.cleaned_data.get('new_location_title')
        new_location_url = self.cleaned_data.get('new_location_url')

        if new_location_title:
            if not new_location_url:
                raise forms.ValidationError('URL needs to be provided for new locations')
        return new_location_url

    def save(self, commit=False):
        """
        Determining whether to create a new
        location or use an existing one
        """
        location = self.cleaned_data.get('location')
        new_location_title = self.cleaned_data.get('new_location_title')
        new_location_room = self.cleaned_data.get('new_location_room')
        if new_location_title:
            location_query = Location.objects.filter(title=new_location_title, room=new_location_room)
            if location_query.count():
                location = location_query[0]
            else:
                location = Location()
                location.title = new_location_title
                location.room = new_location_room
                location.url = self.cleaned_data.get('new_location_url')
                location.save()
            self.instance.location = location
        else:
            if not location:
                raise forms.ValidationError('No existing or new location has been selected')

        e = super(EventInstanceForm, self).save(commit=commit)
        return e

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


class LocationForm(forms.ModelForm):
    """
    Form for adding/creating locations for an EventInstance
    """
    class Meta:
        model = Location
        fields = ('title', 'room', 'url', 'reviewed')
