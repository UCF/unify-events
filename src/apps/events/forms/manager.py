from django.forms import ModelForm
from events.models import Calendar

class CalendarForm(ModelForm):
	class Meta:
		model  = Calendar
		fields = ('name', 'slug')

class CalendarEditorsForm(ModelForm):
	class Meta:
		model  = Calendar
		fields = ('editors',)