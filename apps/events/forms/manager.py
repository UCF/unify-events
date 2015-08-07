import re

from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from taggit.models import Tag

from core.forms import RequiredModelFormSet
from core.utils import generate_unique_slug
from events.forms.fields import InlineLDAPSearchField
from events.forms.widgets import BootstrapSplitDateTimeWidget
from events.functions import is_date_in_valid_range
from events.functions import get_earliest_valid_date
from events.functions import get_latest_valid_date
from events.models import Calendar
from events.models import Event
from events.models import EventInstance
from events.models import Location
from events.models import Category


class ModelFormStringValidationMixin(forms.ModelForm):
    """
    Mixin that trims any string values passed through
    the given form's fields.
    """
    def clean(self):
        cleaned_data = super(ModelFormStringValidationMixin, self).clean()

        for field in cleaned_data:
            val = cleaned_data.get(field)
            if isinstance(val, basestring):
                val = val.strip()
                cleaned_data[field] = val

        return cleaned_data


class CalendarForm(ModelFormStringValidationMixin, forms.ModelForm):
    """
    Form for the Calendar
    """
    editors = InlineLDAPSearchField(queryset=User.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        super(CalendarForm, self).__init__(*args, **kwargs)
        calendar = kwargs['instance']
        # Disable the title field for the main calendar
        if calendar and calendar.is_main_calendar:
            self.fields['title'].widget.attrs['readonly'] = True

    def clean_title(self):
        # Prevent main calendar title from being modified
        calendar = self.instance
        if calendar and calendar.is_main_calendar:
            return calendar.title
        else:
            return self.cleaned_data['title']

    class Meta:
        model = Calendar
        fields = ('title', 'description', 'editors')


class CalendarSubscribeForm(forms.ModelForm):
    """
    Subscribe one or more calendars to another calendar
    """
    calendars = forms.ModelMultipleChoiceField(queryset=Calendar.objects.none(), label='Calendars to subscribe:')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CalendarSubscribeForm, self).__init__(*args, **kwargs)
        self.fields['calendars'].queryset = user.editable_calendars.all()

    class Meta(CalendarForm.Meta):
        model = Calendar
        fields = ('calendars',)


class EventForm(ModelFormStringValidationMixin, forms.ModelForm):
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

    def clean(self):
        self._validate_unique = True
        cleaned_data = super(EventForm, self).clean()

        # Only support the Basic Multilingual Plane on CharFields for mysql
        # utf-8 support
        cleaned_data['title'] = re.sub(r'[^\u0000-\uFFFF]', '', cleaned_data['title'])
        cleaned_data['description'] = re.sub(r'[^\u0000-\uFFFF]', '', cleaned_data['description'])
        cleaned_data['contact_name'] = re.sub(r'[^\u0000-\uFFFF]', '', cleaned_data['contact_name'])

        # Phone number valid characters should be more limited. Note: we aren't
        # trying to determine if the phone number here is actually valid; we
        # just want to limit the allowed characters to basic ASCII.
        cleaned_data['contact_phone'] = re.sub(r'([^\x00-\x7F])', '', cleaned_data['contact_phone'])

        # Delete any cleaned data that are now empty and let the user know
        if not cleaned_data['title']:
            self._errors['title'] = self.error_class(['Please enter a valid title.'])
            del cleaned_data['title']

        if not cleaned_data['description']:
            self._errors['description'] = self.error_class(['Please enter a valid description.'])
            del cleaned_data['description']

        if not cleaned_data['contact_name']:
            self._errors['contact_name'] = self.error_class(['Please enter a valid name.'])
            del cleaned_data['contact_name']

        if not cleaned_data['contact_phone']:
            self._errors['contact_phone'] = self.error_class(['Please enter a valid phone number.'])
            del cleaned_data['contact_phone']

        # Remove '&quot;' and '"' characters from tag phrases, and strip
        # characters that don't match our whitelist.
        tags = cleaned_data['tags']
        for key, tag in enumerate(tags):
            tags[key] = re.sub(r'([^a-zA-Z0-9 -!$#%&+|:?])|(&quot;?)', '', tag)

        return cleaned_data

    class Meta:
        model = Event
        fields = ('calendar', 'title', 'state', 'description', 'contact_name', 'contact_email', 'contact_phone', 'category', 'tags')


class EventInstanceForm(ModelFormStringValidationMixin, forms.ModelForm):
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

        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        until = cleaned_data.get('until')
        location = cleaned_data.get('location')
        new_location_title = cleaned_data.get('new_location_title')
        new_location_url = cleaned_data.get('new_location_url')

        if start and end:
            if start > end:
                self._errors['end'] = self.error_class(['The end day/time must occur after the start day/time'])
            if not is_date_in_valid_range(start.date()):
                self._errors['start'] = self.error_class(['Please provide a start date that falls between %s and %s' % (get_earliest_valid_date(date_format='%m/%d/%Y'), get_latest_valid_date(date_format='%m/%d/%Y'))])
            if not is_date_in_valid_range(end.date()):
                self._errors['end'] = self.error_class(['Please provide a end date that falls between %s and %s' % (get_earliest_valid_date(date_format='%m/%d/%Y'), get_latest_valid_date(date_format='%m/%d/%Y'))])
        else:
            if not start:
                self._errors['start'] = self.error_class(['Please enter a valid date/time, e.g. 11/16/2014 at 12:45 PM'])
            if not end:
                self._errors['end'] = self.error_class(['Please enter a valid date/time, e.g. 11/16/2014 at 12:45 PM'])

        if until:
            if not is_date_in_valid_range(until):
                self._errors['until'] = self.error_class(['Please provide an until date that falls between %s and %s' % (get_earliest_valid_date(date_format='%m/%d/%Y'), get_latest_valid_date(date_format='%m/%d/%Y'))])
            if end.date() >= until:
                self._errors['until'] = self.error_class(['The until date must fall after the end date/time'])

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


class LocationForm(ModelFormStringValidationMixin, forms.ModelForm):
    """
    Form for adding/creating locations for an EventInstance
    """
    class Meta:
        model = Location
        fields = ('title', 'room', 'url', 'reviewed')


class CategoryForm(ModelFormStringValidationMixin, forms.ModelForm):
    """
    Form for adding/creating categories for Events
    """
    class Meta:
        model = Category
        fields = ('title', 'color')


class TagForm(ModelFormStringValidationMixin, forms.ModelForm):
    """
    Form for tags
    """
    class Meta:
        model = Tag
        fields = ('name',)

    def save(self):
        """
        Make sure the slug is updated when the title is changed
        """
        tag = super(TagForm, self).save(commit=False)
        tag.slug = generate_unique_slug(tag.name, Tag, True)
        tag.save()
        return tag
