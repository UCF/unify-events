import logging

from django.views.generic.simple import direct_to_template
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from events.forms.manager import EventForm, EventInstanceForm, EventCopyForm
from events.models import Event, EventInstance, Calendar

log = logging.getLogger(__name__)


@login_required
def create_update(request, event_id=None):
    ctx = {'event': None, 'event_form': None, 'event_instance_formset': None, 'mode': 'create'}
    tmpl = 'events/manager/events/create_update.html'

    # Event Forms
    formset_qs = EventInstance.objects.none()
    formset_extra = 1
    if event_id is not None:
        try:
            ctx['event'] = get_object_or_404(Event, pk=event_id)
            formset_qs = ctx['event'].event_instances.filter(parent=None)
            formset_extra = 0
            if ctx['event'].event_instances.count() == 0:
                formset_extra = 1
            ctx['mode'] = 'update'
        except Event.DoesNotExist:
            return HttpResponseNotFound('The event specified does not exist.')
        else:
            # Is this an event you can edit?
            if not request.user.is_superuser:
                if ctx['event'].calendar not in request.user.calendars:
                    return HttpResponseForbidden('You cannot modify the specified event.')


    ## Can't use user.calendars here because ModelChoiceField expects a queryset
    user_calendars = Calendar.objects.filter(owner=request.user)
    EventInstanceFormSet = modelformset_factory(EventInstance,
                                                form=EventInstanceForm,
                                                extra=formset_extra,
                                                can_delete=True,
                                                max_num=12)

    # TODO: add event instance formset
    if request.method == 'POST':
        ctx['event_form'] = EventForm(request.POST,
                                      instance=ctx['event'],
                                      prefix='event',
                                      user_calendars=user_calendars)
        ctx['event_instance_formset'] = EventInstanceFormSet(request.POST,
                                                          prefix='event_instance',
                                                          queryset=formset_qs)

        if ctx['event_form'].is_valid() and ctx['event_instance_formset'].is_valid():
            event = ctx['event_form'].save(commit=False)
            event.creator = request.user
            try:
                event.save()
                ctx['event_form'].save_m2m()
            except Exception,e:
                log.error(str(e))
                messages.error(request,'Saving event failed.')
            else:
                instances = ctx['event_instance_formset'].save(commit=False)
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
        ctx['event_form'] = EventForm(prefix='event', instance=ctx['event'], user_calendars=user_calendars)
        ctx['event_instance_formset'] = EventInstanceFormSet(queryset=formset_qs, prefix='event_instance',)

    return direct_to_template(request, tmpl, ctx)


@login_required
def update_state(request, event_id=None, state=None):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound('The event specified does not exist.')
    else:
        if not request.user.is_superuser and event.calendar not in request.user.calendars:
                return HttpResponseForbidden('You cannot modify the specified event.')
        event.state = state
        try:
            event.save()
        except Exception, e:
            log(str(e))
            messages.error(request, 'Saving event failed.')
        else:
            messages.success(request, 'Event successfully updated.')
            return HttpResponseRedirect(reverse('dashboard', kwargs={'calendar_id': event.calendar.id}))


@login_required
def delete(request, event_id=None):
    try:
        event = Event.objects.get(pk=event_id)
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


@login_required
def copy(request, event_id):
    ctx = {'event': None, 'form': None}
    tmpl = 'events/manager/events/copy.html'

    try:
        ctx['event'] = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return HttpResponseNotFound('Event specified does not exist.')
    else:
        if not request.user.is_superuser and ctx['event'].calendar not in request.user.calendars:
            return HttpResponseForbidden('You cannot copy the specified event.')

        user_calendars = request.user.calendars.exclude(pk=ctx['event'].calendar.id)

        if request.method == 'POST':
            ctx['form'] = EventCopyForm(request.POST, calendars=user_calendars)
            if ctx['form'].is_valid():
                error = False
                for calendar in ctx['form'].cleaned_data['calendars']:
                    try:
                        ctx['event'].copy(calendar=calendar)
                    except Exception, e:
                        messages.error(request, 'Unable to copy even to %s' % calendar.name)
                        error = True
                if not error:
                    messages.success(request, 'Event successfully copied.')
                return HttpResponseRedirect(reverse('dashboard'))
        else:
            ctx['form'] = EventCopyForm(calendars=user_calendars)
    return direct_to_template(request,tmpl,ctx)