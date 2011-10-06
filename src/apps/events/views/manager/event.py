from ..events.forms.manager      import EventForm,EventInstanceForm
from ..events.models             import Event,EventInstance
from django.contrib              import messages
from django.views.generic.simple import direct_to_template
from django.forms.models         import modelformset_factory

def create_update(request, id=None):
	ctx  = {'form':None,'formset':None}
	tmpl = 'events/manager/events/create_update_event.html'


	EventInstanceFormSet = modelformset_factory(EventInstance,form=EventInstanceForm)

	if id is None:
		if request.method == 'POST':
			ctx['form']    = EventForm(request.POST,prefix='event')
			ctx['formset'] = EventInstanceFormSet(request.POST,prefix='event_instance')

			if ctx['form'].is_valid() and ctx['formset'].is_valid():
				event = ctx['form'].save()
				instances = ctx['formset'].save(commit=False)
				for instance in instances:
					instance.event = event
					instance.save()
				
		else:
			ctx['form']    = EventForm(prefix='event')
			ctx['formset'] = EventInstanceFormSet(queryset=Event.objects.none(),prefix='event_instance')
	else:
		try:
			event = Event.objects.get(pk = id)
		except Event.DoesNotExist:
			messages.error('Event does not exist')
			# Redirect
		else:
			if request.method == 'POST':
				ctx['form']    = EventForm(request.POST,instance=event,prefix='event')
				ctx['formset'] = EventInstanceFormSet(request.POST,queryset=event.instances.all(),prefix='event_instance')

				if ctx['form'].is_valid() and ctx['formset'].is_valid():
					event = ctx['form'].save()
					instances = ctx['formset'].save(commit=False)
					for instance in instances:
						if instance.event is None:
							instance.event = event
							instance.save()
			else:
				ctx['form']    = EventForm(instance=event,prefix='event')
				ctx['formset'] = EventInstanceFormSet(queryset=event.instances.al(),prefix='event_instance')
	return direct_to_template(request,tmpl,ctx)