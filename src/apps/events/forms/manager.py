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
		fields = ('name', 'slug','public','editors', 'subscriptions')

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
		fields = ('title', 'description','calendar')

class EventInstanceForm(forms.ModelForm):

	AMPM_CHOICES = (
		('am', 'AM'),
		('pm', 'PM')
	)

	start_hour   = forms.ChoiceField(choices=list((i,i) for i in range(0,11)))
	start_minute = forms.ChoiceField(choices=list((i,i) for i in range(0,60,15)))
	start_ampm   = forms.ChoiceField(choices=AMPM_CHOICES)

	end_hour   = forms.ChoiceField(choices=list((i,i) for i in range(0,11)))
	end_minute = forms.ChoiceField(choices=list((i,i) for i in range(0,60,15)))
	end_ampm   = forms.ChoiceField(choices=AMPM_CHOICES)

	interval = forms.ChoiceField(choices=EventInstance.Recurs.choices,label='Recurrence')

	def clean(self):
		cleaned_data = self.cleaned_data

		# Combine date and time fields
		start        = cleaned_data.get('start')
		start_hour   = cleaned_data.get('start_hour')
		start_minute = cleaned_data.get('start_minute')
		start_ampm   = cleaned_data.get('start_ampm')
		end   = cleaned_data.get('end')
		end_hour   = cleaned_data.get('end_hour')
		end_minute = cleaned_data.get('end_minute')
		end_ampm   = cleaned_data.get('end_ampm')

		try:
			start = datetime(start.year,start.month,start.day,int(start_hour),int(start_minute))
			if start_ampm == 'pm':
				start = start + timedelta(seconds=43200) # 12 hours
		except Exception, e:
			raise forms.ValidationError('Invalid start date: Must be in the form MM/DD/YYYY')

		try:
			end = datetime(end.year,end.month,end.day,int(end_hour),int(end_minute))
			if end_ampm == 'pm':
				end = end + timedelta(seconds=43200) # 12 hours
		except Exception, e:
			print str(e)
			raise forms.ValidationError('Invalid end date: Must be in the form MM/DD/YYYY')
		
		cleaned_data['start'] = start
		cleaned_data['end']   = end

		return cleaned_data

	class Meta:
		model  = EventInstance
		fields = ('location', 'start', 'end', 'interval', 'limit')
		widgets = {
			'start': forms.TextInput(attrs={'class':'datepicker'}),
			'end'  : forms.TextInput(attrs={'class':'datepicker'})
		}