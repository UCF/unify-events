from copy import deepcopy
import re

from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError
from events.models.promotion import Promotion
from taggit.models import Tag


from core.forms import RequiredModelFormSet
from core.utils import generate_unique_slug
from events.forms.fields import InlineLDAPSearchField
from events.forms.fields import CustomImageWidget
from events.forms.widgets import BootstrapSplitDateTimeWidget
from events.forms.widgets import TaggitField
from events.forms.widgets import Wysiwyg
from events.forms.fields import CalendarChoiceField
from events.functions import is_date_in_valid_range
from events.functions import get_earliest_valid_date
from events.functions import get_latest_valid_date
from events.models import Calendar
from events.models import Event
from events.models import EventInstance
from events.models import Location
from events.models import Category

import settings


class ModelFormStringValidationMixin(forms.ModelForm):
    """
    Mixin that trims any string values passed through
    the given form's fields.
    """
    def clean(self):
        cleaned_data = super(ModelFormStringValidationMixin, self).clean()

        for field in cleaned_data:
            val = cleaned_data.get(field)
            if isinstance(val, str):
                val = val.strip()
                cleaned_data[field] = val

        return cleaned_data


class ModelFormUtf8BmpValidationMixin(forms.ModelForm):
    """
    Mixin that strips characters outside of the Basic Multilingual Plane
    out of string values.
    """
    def clean(self):
        cleaned_data = super(ModelFormUtf8BmpValidationMixin, self).clean()
        cleaned_data_copy = deepcopy(cleaned_data)  # Make a copy because python won't let you modify a dict while it's being iterated

        form_fields = self.fields

        for field, val in cleaned_data.items():
            required = form_fields[field].required

            if isinstance(val, str):
                cleaned_data_copy[field] = re.sub(r'[^\u0000-\uD7FF\uE000-\uFFFF]', '', cleaned_data_copy[field])

                # Delete any cleaned data that are now empty and let the user know
                if not cleaned_data_copy[field]:
                    if required:
                        self._errors[field] = self.error_class(['Sorry, special characters are not permitted here. Please enter a different value.'])
                    del cleaned_data_copy[field]

        return cleaned_data_copy


class CalendarForm(ModelFormStringValidationMixin, ModelFormUtf8BmpValidationMixin, forms.ModelForm):
    """
    Form for the Calendar
    """
    def __init__(self, *args, **kwargs):
        super(CalendarForm, self).__init__(*args, **kwargs)
        calendar = kwargs['instance']
        # Disable the title field for the main calendar
        if calendar and calendar.is_main_calendar:
            self.fields['title'].widget.attrs['readonly'] = True

    def clean_title(self):
        # Prevent main calendar title from being modified
        calendar = self.instance
        title = self.cleaned_data['title']

        if title.lower() in settings.DISALLOWED_CALENDAR_TITLES:
            #TODO Make a help section explaining which titles are not allowed and link to it.
            raise ValidationError(f"The calendar title you entered is not allowed.")

        if calendar and calendar.is_main_calendar:
            return calendar.title
        else:
            return self.cleaned_data['title']

    class Meta:
        model = Calendar
        fields = (
            'title',
            'description',
            'active',
            'trusted',
            'desktop_header_image',
            'mobile_header_image',
        )
        widgets = {
            'desktop_header_image': CustomImageWidget,
            'mobile_header_image': CustomImageWidget
        }


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


class EventForm(ModelFormStringValidationMixin, ModelFormUtf8BmpValidationMixin, forms.ModelForm):
    """
    Form for an Event
    """
    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial')
        user_calendars = initial.pop('user_calendars')
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['calendar'].queryset = user_calendars


        self.fields['title'].widget = forms.TextInput(attrs={"spellcheck": "true"})
        self.fields['description'].widget = Wysiwyg()
        self.fields['tags'].widget = TaggitField()

        instance = kwargs['instance']
        if instance and instance.created_from:
            if instance.created_from.title is instance.title:
                self.fields['new_title'] = forms.CharField(required=False, initial=instance.title)
                self.fields['new_title'].widget.attrs['disabled'] = 'disabled'

            if instance.created_from.description is instance.description:
                self.fields['new_description'] = forms.CharField(required=False,
                                                                 initial=instance.description,
                                                                 widget=forms.Textarea(attrs={'disabled': 'disabled', 'class': 'wysiwyg'}))

        self.fields['submit_to_calendar'] = CalendarChoiceField(queryset=Calendar.objects.all(), required=False)
        obj = self.instance
        copied_event = obj.get_copied_event()
        if copied_event is not None:
            self.fields['submit_to_calendar'].initial = copied_event.calendar


    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Event Title'}))
    calendar = forms.ModelChoiceField(queryset=Calendar.objects.none(), empty_label=None)
    registration_checkbox = forms.BooleanField(required=False)

    def clean(self):
        self._validate_unique = True
        cleaned_data = super(EventForm, self).clean()

        registration_checkbox = cleaned_data.get('registration_checkbox')
        registration_link = cleaned_data.get('registration_link')
        registration_info = cleaned_data.get('registration_info')

        if not registration_checkbox:
            cleaned_data['registration_link'] = None
            cleaned_data['registration_info'] = None

        if registration_checkbox and registration_info == None:
            cleaned_data['registration_info'] = None

        # Remove '&quot;' and '"' characters from tag phrases, and strip
        # characters that don't match our whitelist.
        tags = cleaned_data.get('tags', [])

        if len(tags) > 5:
            self.errors['tags'] = self.error_class(['Please provide no more than 5 tags that best describe your event.'])

        for key, tag in enumerate(tags):
            tags[key] = re.sub(r'([^a-zA-Z0-9 -!$#%&+|:?\'])|(&quot;?)', '', tag)

        if registration_checkbox and not registration_link:
            self._errors['registration_link'] = self.error_class(['A registration link is required if the registration checkbox is checked.'])

        return cleaned_data

    class Meta:
        model = Event
        fields = ('calendar', 'title', 'state', 'description', 'contact_name', 'contact_email', 'contact_phone', 'category', 'tags', 'registration_link', 'registration_info')


class EventInstanceForm(ModelFormStringValidationMixin, ModelFormUtf8BmpValidationMixin, forms.ModelForm):
    """
    Form for the EventInstance
    """
    start = forms.DateTimeField(
        widget=BootstrapSplitDateTimeWidget(
            attrs={
                'date_class': 'form-control field-date',
                'time_class': 'form-control field-time',
                'date_placeholder': 'mm/dd/yyyy',
                'time_placeholder': '12:00 AM',
                'autocomplete': 'off'
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
                'date_class': 'form-control field-date',
                'time_class': 'form-control field-time',
                'date_placeholder': 'mm/dd/yyyy',
                'time_placeholder': '12:00 AM',
                'autocomplete': 'off'
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
    physical_checkbox = forms.BooleanField(required=False)
    virtual_checkbox = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(EventInstanceForm, self).clean()

        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        until = cleaned_data.get('until')
        location = cleaned_data.get('location')
        virtual_url = cleaned_data.get('virtual_url')
        new_location_title = cleaned_data.get('new_location_title')
        new_location_url = cleaned_data.get('new_location_url')
        physical_checkbox = cleaned_data.get('physical_checkbox')
        virtual_checkbox = cleaned_data.get('virtual_checkbox')

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

        # at this point, 'location' is none if it's not set to a defined location
        # (new locations are not created and saved as 'location' yet)

        # if p.checkbox true and no location, check for new location title
        if physical_checkbox and not location:
            if new_location_title:
                if not new_location_url:
                    self._errors['new_location_url'] = self.error_class(['URL needs to be provided for new locations'])
            # if p.checkbox true and no location and no new loc. title, throw error
            else:
                self._errors['location'] = self.error_class(['No location was specified'])

        # if v.checkbox true and no virtual_url, throw error
        if virtual_checkbox and not virtual_url:
            self._errors['virtual_url'] = self.error_class(['Please provide a virtual location URL'])

        # if no location and no virtual location and no new location title, throw error
        # this error will also show up if checkbox(es) are checked with no values in the field(s)
        if not location and not virtual_url and not new_location_title:
                raise ValidationError('Either a physical or virtual location is required.')

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
        if not location and new_location_title:
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
        fields = ('start', 'end', 'interval', 'until', 'location', 'virtual_url')
        widgets = {
            'location': forms.TextInput()
        }


"""
Define formsets for EventInstances, for use within Event forms.

Two separate formsets are defined for Create and Update views to allow for
a different number of extra blank forms (we want a blank form for the Event
Create view, but not for the Event Update view).
"""
EventInstanceCreateFormSet = inlineformset_factory(Event,
                                                   EventInstance,
                                                   form=EventInstanceForm,
                                                   formset=RequiredModelFormSet,
                                                   extra=1,
                                                   max_num=12)

EventInstanceUpdateFormSet = inlineformset_factory(Event,
                                                   EventInstance,
                                                   form=EventInstanceForm,
                                                   formset=RequiredModelFormSet,
                                                   extra=0,
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


class LocationForm(ModelFormStringValidationMixin, ModelFormUtf8BmpValidationMixin, forms.ModelForm):
    """
    Form for adding/creating locations for an EventInstance
    """
    class Meta:
        model = Location
        fields = ('title', 'room', 'url', 'reviewed')


class CategoryForm(ModelFormStringValidationMixin, ModelFormUtf8BmpValidationMixin, forms.ModelForm):
    """
    Form for adding/creating categories for Events
    """
    class Meta:
        model = Category
        fields = ('title', 'color')


class TagForm(ModelFormStringValidationMixin, ModelFormUtf8BmpValidationMixin, forms.ModelForm):
    """
    Form for tags
    """
    class Meta:
        model = Tag
        fields = ('name', )

    def save(self):
        """
        Make sure the slug is updated when the title is changed
        """
        tag = super(TagForm, self).save(commit=False)
        tag.slug = generate_unique_slug(tag.name, Tag, True)
        tag.save()
        return tag

class PromotionForm(forms.ModelForm):
    """
    Form for promotions
    """
    class Meta:
        model = Promotion
        fields = ('title', 'image', 'alt_text', 'url', 'active')
