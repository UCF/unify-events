from django.contrib.auth.models import User
from events.models              import Calendar, Profile, Event, EventInstance
from django                     import forms
from datetime                   import datetime,timedelta
from django.contrib.auth.models import User

class CalendarForm(forms.ModelForm):

	subscriptions = forms.ModelMultipleChoiceField(queryset=Calendar.objects.filter(public=True),required=False)
	editors       = forms.ModelMultipleChoiceField(queryset=User.objects.none(),required=False)

	class Meta:
		model  = Calendar
		fields = ('name', 'slug','public','shared','editors', 'subscriptions')

class UserForm(forms.ModelForm):
	class Meta:
		model  = User
		fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
	class Meta:
		model  = Profile
		fields = ('display_name',)

class EventForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		user_calendars = kwargs.pop('user_calendars')
		super(EventForm, self).__init__(*args, **kwargs)
		self.fields['calendar'].queryset = user_calendars

	calendar = forms.ModelChoiceField(queryset=Calendar.objects.none())

	class Meta:
		model  = Event
		fields = ('title', 'description','calendar','image')

class EventInstanceForm(forms.ModelForm):

	AMPM_CHOICES = (
		('am', 'AM'),
		('pm', 'PM')
	)

	start = forms.SplitDateTimeField()
	end   = forms.SplitDateTimeField()

	interval = forms.ChoiceField(choices=EventInstance.Recurs.choices,label='Recurrence')

	class Meta:
		model  = EventInstance
		fields = ('location', 'start', 'end', 'interval', 'limit')
		widgets = {
			'start': forms.TextInput(attrs={'class':'datepicker'}),
			'end'  : forms.TextInput(attrs={'class':'datepicker'})
		}