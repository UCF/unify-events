from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from taggit.models import Tag
from taggit.forms import TagField

from core.forms import RequiredModelFormSet
from events.models import Calendar
from events.models import Event
from events.models import EventInstance
from events.models import Location
from events.models import Category
from events.forms.fields import InlineLDAPSearchField
from events.forms.widgets import BootstrapSplitDateTimeWidget


class CalendarForm(forms.ModelForm):
    """
    Form for the Calendar
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
        initial = kwargs.pop('initial')
        user_calendars = initial.pop('user_calendars')
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
        fields = ('calendar', 'title', 'state', 'description', 'contact_name', 'contact_email', 'contact_phone', 'category', 'tags')


class EventInstanceForm(forms.ModelForm):
    """
    Form for the EventInstance
    """
    start = forms.DateTimeField(
        widget=BootstrapSplitDateTimeWidget(
            attrs={
                'date_class': 'field-date',
                'time_class': 'field-time',
                'date_placeholder': 'mm/dd/yyyy',
                'time_placeholder': '12:00 AM'
            }
        ),
        input_formats=[
            '%m/%d/%Y %I:%M %p', # '10/25/2006 2:30 PM'
            '%m/%d/%Y %I:%M',    # '10/25/2006 14:30'
        ],
    )
    end = forms.DateTimeField(
        widget=BootstrapSplitDateTimeWidget(
            attrs={
                'date_class': 'field-date',
                'time_class': 'field-time',
                'date_placeholder': 'mm/dd/yyyy',
                'time_placeholder': '12:00 AM'
            }
        ),
        input_formats=[
            '%m/%d/%Y %I:%M %p', # '10/25/2006 2:30 PM'
            '%m/%d/%Y %I:%M',    # '10/25/2006 14:30'
        ],
    )

    until = forms.DateField(required=False)
    new_location_title = forms.CharField(required=False)
    new_location_room = forms.CharField(required=False)
    new_location_url = forms.URLField(required=False)

    def clean(self):
        cleaned_data = super(EventInstanceForm, self).clean()

        location = cleaned_data.get('location')
        new_location_title = cleaned_data.get('new_location_title')
        new_location_url = cleaned_data.get('new_location_url')

        if not location:
            if new_location_title:
                if not new_location_url:
                    self._errors['new_location_url'] = self.error_class(['URL needs to be provided for new locations'])
            else:
                self._errors['location'] = self.error_class(['No location was specified'])

        return cleaned_data

    def save(self, commit=False):
        """
        Determining whether to create a new
        location or use an existing one
        """
        location = self.cleaned_data.get('location')
        new_location_title = self.cleaned_data.get('new_location_title')
        new_location_room = self.cleaned_data.get('new_location_room')
        new_location_url = self.cleaned_data.get('new_location_url')
        if not location:
            location_query = Location.objects.filter(title=new_location_title, room=new_location_room)
            if location_query.count():
                location = location_query[0]
            else:
                location = Location()
                location.title = new_location_title
                location.room = new_location_room
                location.url = new_location_url
                location.save()
            self.instance.location = location

        event_instance = super(EventInstanceForm, self).save(commit=commit)
        return event_instance

    class Meta:
        model = EventInstance
        fields = ('start', 'end', 'interval', 'until', 'location')


EventInstanceFormSet = inlineformset_factory(Event,
                                             EventInstance,
                                             form=EventInstanceForm,
                                             formset=RequiredModelFormSet,
                                             extra=1,
                                             max_num=12)


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


class CategoryForm(forms.ModelForm):
    """
    Form for adding/creating categories for Events
    """
    class Meta:
        model = Category
        fields = ('title', 'color')


class TagForm(forms.ModelForm):
    """
    Form for tags
    """
    class Meta:
        model = Tag
        fields = ('name',)
