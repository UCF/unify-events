from django.contrib.auth.decorators  import login_required
from events.forms.manager            import EventForm,EventInstanceForm
from events.models                   import Event,EventInstance,Calendar
from django.contrib                  import messages
from django.views.generic.simple     import direct_to_template
from django.forms.models             import modelformset_factory
from django.db.models                import Q
from django.http                     import HttpResponseNotFound, HttpResponseForbidden,HttpResponseRedirect
from django.core.urlresolvers        import reverse
import logging

log = logging.getLogger(__name__)


@login_required
def create_update(request, id=None):
	ctx  = {'event':None,'event_form':None,'event_formset':None,'mode':'create'}
	tmpl = 'events/manager/events/create_update.html'

	# Event Forms
	formset_qs    = EventInstance.objects.none()
	formset_extra = 1
	if id is not None:
		try:
			ctx['event']  = Event.objects.get(pk=id)
			formset_qs    = ctx['event'].instances.filter(parent=None)
			formset_extra = 0
			if ctx['event'].instances.count() == 0:
				formset_extra = 1
			ctx['mode']   = 'update'
		except Event.DoesNotExist:
			return HttpResponseNotFound('The event specified does not exist.')
		else:
			# Is this an event you can edit?
			if not request.user.is_superuser:
				if ctx['event'].calendar not in request.user.calendars:
					return HttpResponseForbidden('You cannot modify the specified event.')


	## Can't use user.calendars here because ModelChoiceField expects a queryset
	user_calendars = Calendar.objects.filter(Q(creator=request.user)|Q(editors=request.user))
	EventInstanceFormSet = modelformset_factory(
							EventInstance,
							form=EventInstanceForm,
							extra=formset_extra,
							can_delete=True)
	if request.method == 'POST':
		ctx['event_form']    = EventForm(request.POST,request.FILES,instance=ctx['event'],prefix='event',user_calendars=user_calendars)
		ctx['event_formset'] = EventInstanceFormSet(request.POST,prefix='event_instance',queryset=formset_qs)

		if ctx['event_form'].is_valid() and ctx['event_formset'].is_valid():
			event = ctx['event_form'].save(commit=False)
			event.creator = request.user
			try:
				event.save()
				ctx['event_form'].save_m2m()
			except Exception,e:
				log.error(str(e))
				messages.error(request,'Saving event failed.')
			else:
				instances = ctx['event_formset'].save(commit=False)
				error = False
				for instance in instances:
					instance.event = event
					try:
						instance.save()
					except Exception,e:
						log.error(str(e))
						messages.error(request,'Saving event instance failed.')
						error = True
						break
				if not error:
					messages.success(request, 'Event successfully saved')
				
			return HttpResponseRedirect(reverse('dashboard'))
	else:
		ctx['event_form']    = EventForm(prefix='event',instance=ctx['event'],user_calendars=user_calendars)
		ctx['event_formset'] = EventInstanceFormSet(queryset=formset_qs,prefix='event_instance',)

	return direct_to_template(request,tmpl,ctx)

@login_required
def update_state(request, id=None, state=None):
	try:
		event = Event.objects.get(pk=id)
	except Event.DoesNotExist:
		return HttpResponseNotFound('The event specified does not exist.')
	else:
		if not request.user.is_superuser:
			if event.calendar not in request.user.calendars:
				return HttpResponseForbidden('You cannot modify the specified event.')
		event.state = state
		try:
			event.save()
		except Exception, e:
			log(str(e))
			messages.error(request, 'Saving event failed.')
		else:
			messages.success(request, 'Event successfully updated.')
			if event.on_owned_calendar(request.user):
				return HttpResponseRedirect(reverse('dashboard', kwargs={'calendar_id':event.calendar.id}))
			else:
				return HttpResponseRedirect(reverse('dashboard'))

@login_required
def delete(request, id=None):
	try:
		event = Event.objects.get(pk=id)
	except Event.DoesNotExist:
		return HttpResponseNotFound('The event specified does not exist.')
	else:
		if not request.user.is_superuser:
			if event.calendar not in request.user.calendars:
				return HttpResponseForbidden('You cannot modify the specified event.')
		try:
			event.delete()
		except Exception, e:
			log(str(e))
			messages.error(request, 'Deleting event failed.')
		else:
			messages.success(request, 'Event successfully deleted.')
			return HttpResponseRedirect(reverse('dashboard', kwargs={'calendar_id':event.calendar.id}))