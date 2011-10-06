from django.forms               import ModelForm
from django.contrib.auth.models import User
from events.models              import Calendar, Profile, Event, EventInstance

class CalendarForm(ModelForm):
	class Meta:
		model  = Calendar
		fields = ('name', 'slug')

class CalendarEditorsForm(ModelForm):
	class Meta:
		model  = Calendar
		fields = ('editors',)

class UserForm(ModelForm):
	class Meta:
		model  = User
		fields = ('first_name', 'last_name', 'email')

class ProfileForm(ModelForm):
	class Meta:
		model  = Profile
		fields = ('display_name',)

class EventForm(ModelForm):
	class Meta:
		model  = Event
		fields = ('title', 'description','calendar')

class EventInstanceForm(ModelForm):
	class Meta:
		model  = EventInstance
		fields = ('location', 'start', 'end', 'limit',)