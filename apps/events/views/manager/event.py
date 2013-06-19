import logging

from django.views.generic.simple import direct_to_template
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from events.forms.manager import EventForm, EventCopyForm
from events.models import Event, EventInstance, Calendar

log = logging.getLogger(__name__)


@login_required
def create_update(request, id=None):
    ctx = {'event': None, 'form': None, 'mode': 'create'}
    tmpl = 'events/manager/events/create_update.html'

    # Event Forms
    formset_qs = Event.objects.none()
    if id is not None:
        try:
            ctx['event'] = get_object_or_404(Event, pk=id)
            ctx['mode'] = 'update'
        except Event.DoesNotExist:
            return HttpResponseNotFound('The event specified does not exist.')
        else:
            # Is this an event you can edit?
            if not request.user.is_superuser:
                if ctx['event'].calendar not in request.user.calendars:
                    return HttpResponseForbidden('You cannot modify the specified event.')


    ## Can't use user.calendars here because ModelChoiceField expects a queryset
    user_calendars = Calendar.objects.filter(Q(owner=request.user))

    # TODO: add event instance formset
    if request.method == 'POST':
        ctx['form'] = EventForm(request.POST,
                                request.FILES,
                                instance=ctx['event'],
                                prefix='event',
                                user_calendars=user_calendars)

        if ctx['form'].is_valid():
            event = ctx['form'].save(commit=False)
            event.owner = request.user
            event.save()

            return HttpResponseRedirect(reverse('dashboard'))
    else:
        ctx['form'] = EventForm(prefix='event', instance=ctx['event'], user_calendars=user_calendars)

    return direct_to_template(request, tmpl, ctx)


@login_required
def update_state(request, id=None, state=None):
    try:
        event = Event.objects.get(pk=id)
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


@login_required
def copy(request, id):
    ctx = {'event': None, 'form': None}
    tmpl = 'events/manager/events/copy.html'

    try:
        ctx['event'] = Event.objects.get(pk=id)
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