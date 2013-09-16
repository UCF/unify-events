import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseNotFound, HttpResponseForbidden,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404

from events.models import Calendar
from events.forms.manager import CalendarForm

log = logging.getLogger(__name__)


@login_required
def create_update(request, calendar_id=None):
    ctx = {'form': None, 'mode': 'create', 'calendar': None}
    if len(request.user.calendars.all()) == 0 and request.user.first_login:
        tmpl = 'events/manager/firstlogin/calendar_create.html'
    else:
        tmpl = 'events/manager/calendar/create_update.html'

    if calendar_id is not None:
        ctx['mode'] = 'update'
        try:
            ctx['calendar'] = Calendar.objects.get(pk=calendar_id)
        except Calendar.DoesNotExist:
            return HttpResponseNotFound('The calendar specified does not exist.')
        else:
            if not request.user.is_superuser and ctx['calendar'] not in request.user.editable_calendars:
                return HttpResponseForbidden('You cannot modify the specified calendar.')

    if request.method == 'POST':
        ctx['form'] = CalendarForm(request.POST, instance=ctx['calendar'])
        if ctx['form'].is_valid():
            calendar = ctx['form'].save(commit=False)
            if not calendar.owner:
                calendar.owner = request.user
            calendar.save()
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        ctx['form'] = CalendarForm(instance=ctx['calendar'])

    return direct_to_template(request, tmpl, ctx)

@login_required
def delete(request, calendar_id=None):
    try:
        calendar = Calendar.objects.get(pk=calendar_id)
    except Calendar.DoesNotExist:
        return HttpResponseNotFound('The calendar specified does not exist')
    else:
        if not request.user.is_superuser and calendar not in request.user.calendars:
            return HttpResponseForbidden('You cannot modify the specified calendar.')
        try:
            calendar.delete()
        except Exception, e:
            log.error(str(e))
            messages.error(request, 'Deleting calendar failed.')
        else:
            messages.success(request, 'Calendar successfully deleted.')
    return HttpResponseRedirect(reverse('dashboard'))

@login_required
def add_update_user(request, calendar_id=None, username=None, role=None):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    user = get_object_or_404(User, username=username)
    if calendar not in request.user.editable_calendars or not role:
        return HttpResponseForbidden('Cannot modify permissions.')
    if user == calendar.owner:
        return HttpResponseForbidden('Cannot give Owner a different role through this request.')
    if role == 'admin':
        calendar.editors.remove(user)
        calendar.admins.add(user)
    elif role == 'editor':
        calendar.admins.remove(user)
        calendar.editors.add(user)
    else:
        return HttpResponseForbidden('Not a legitimate role value.')
    calendar.save()
    url_name = 'calendar-update'
    if request.user == user and role == 'editor':
        url_name = 'dashboard'
    return HttpResponseRedirect(reverse(url_name, args=(calendar_id,)))

@login_required
def delete_user(request, calendar_id=None, username=None):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    user = get_object_or_404(User, username=username)
    if calendar not in request.user.editable_calendars:
        return HttpResponseForbidden('Cannot modify permissions.')
    calendar.admins.remove(user)
    calendar.editors.remove(user)
    calendar.save()
    return HttpResponseRedirect(reverse('calendar-update', args=(calendar_id,)))

@login_required
def reassign_ownership(request, calendar_id=None, username=None):
    calendar = get_object_or_404(Calendar, pk=calendar_id)
    user = get_object_or_404(User, username=username)
    if calendar not in request.user.editable_calendars:
        return HttpResponseForbidden('Cannot modify permissions.')
    calendar.admins.add(calendar.owner)
    calendar.owner = user
    calendar.admins.remove(user)
    calendar.editors.remove(user)
    calendar.save()
    return HttpResponseRedirect(reverse('calendar-update', args=(calendar_id,)))

@login_required
def subscribe_to_calendar(request, calendar_id=None, subscribing_calendar_id=None):
    try:
        calendar = Calendar.objects.get(pk=calendar_id)
        subscribing_calendar = Calendar.objects.get(pk=subscribing_calendar_id)
    except Calendar.DoesNotExist:
        return HttpResponseNotFound('One of the specified calendars does not exist.')
    else:
        if calendar not in request.user.calendars:
            return HttpResponseForbidden('You cannot modify the specified calendar.')
        try:
            subscribing_calendar.subscriptions.add(calendar)
        except Exception, e:
            log.error(str(e))
            messages.error(request, 'Adding calendar to subscribing list failed.')
        else:
            messages.success(request, 'Calendar successfully subscribed to.')
    return HttpResponseRedirect(reverse('calendar-update', args=(calendar_id,)))

@login_required
def unsubscribe_from_calendar(request, calendar_id=None, subscribed_calendar_id=None):
    try:
        calendar = Calendar.objects.get(pk=calendar_id)
        subscribed_calendar = Calendar.objects.get(pk=subscribed_calendar_id)
    except Calendar.DoesNotExist:
        return HttpResponseNotFound('One of the specified calendars does not exist.')
    else:
        if calendar not in request.user.calendars:
            return HttpResponseForbidden('You cannot modify the specified calendar.')
        try:
            calendar.subscriptions.remove(subscribed_calendar)
        except Exception, e:
            log.error(str(e))
            messages.error(request, 'Removing subscribed calendar failed.')
        else:
            messages.success(request, 'Calendar successfully unsubscribed.')
    return HttpResponseRedirect(reverse('calendar-update', args=(calendar_id,)))