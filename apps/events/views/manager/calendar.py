import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from core.views import SuccessUrlReverseKwargsMixin
from core.views import FirstLoginTemplateMixin
from core.views import SuperUserRequiredMixin
from core.views import DeleteSuccessMessageMixin

from events.models import Calendar
from events.forms.manager import CalendarForm

log = logging.getLogger(__name__)


class CalendarUserValidationMixin(object):
    """
    Require that the user accessing the calendar is either a superuser
    or owns the requested calendar.

    Return 403 Forbidden if false.
    """
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser and self.get_object() not in self.request.user.owned_calendars.all():
            return HttpResponseForbidden('You cannot modify the specified calendar.')
        else:
            return super(CalendarUserValidationMixin, self).dispatch(request, *args, **kwargs)



class CalendarCreate(FirstLoginTemplateMixin, SuccessMessageMixin, CreateView):
    form_class = CalendarForm
    model = Calendar
    success_message = '%(title)s was created successfully.'
    success_url = reverse_lazy('dashboard')
    template_name = 'events/manager/calendar/create.html'

    def form_valid(self, form):
        """
        Set the calendar owner when validating the form.
        """
        self.object = form.save()
        self.object.owner = self.request.user
        return super(CalendarCreate, self).form_valid(form)


class CalendarDelete(DeleteSuccessMessageMixin, CalendarUserValidationMixin, DeleteView):
    model = Calendar
    success_message = 'Calendar was successfully deleted.'
    success_url = reverse_lazy('dashboard')
    template_name = 'events/manager/calendar/delete.html'


class CalendarUpdate(SuccessMessageMixin, SuccessUrlReverseKwargsMixin, CalendarUserValidationMixin, UpdateView):
    form_class = CalendarForm
    model = Calendar
    success_message = '%(title)s was updated successfully.'
    template_name = 'events/manager/calendar/update.html'
    success_view_name = 'calendar-update'


class CalendarUserUpdate(DetailView):
    # form_class = CalendarForm
    model = Calendar
    # success_message = 'Calendar users updated successfully.'
    template_name = 'events/manager/calendar/update/update-users.html'

    # # TODO: use SuccessUrlReverseKwargsMixin
    # def get_success_url(self):
    #     return reverse_lazy('calendar-update-users', kwargs = {'pk' : self.object.pk, })


class CalendarSubscriptionsUpdate(DetailView):
    model = Calendar
    template_name = 'events/manager/calendar/update/update-subscriptions.html'


class CalendarList(SuperUserRequiredMixin, ListView):
    context_object_name = 'calendars'
    model = Calendar
    paginate_by = 25
    template_name = 'events/manager/calendar/list.html'



@login_required
def add_update_user(request, calendar_id, username, role):
    calendar = get_object_or_404(Calendar, pk=calendar_id)

    if not request.user.is_superuser and calendar not in request.user.editable_calendars:
        return HttpResponseForbidden('You cannot add/update users to the specified calendar.')

    user = get_object_or_404(User, username=username)
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
    if request.user == user and role == 'editor' and not request.user.is_superuser:
        url_name = 'dashboard'

    return HttpResponseRedirect(reverse(url_name, kwargs={'calendar_id': calendar_id}))

@login_required
def delete_user(request, calendar_id, username):
    calendar = get_object_or_404(Calendar, pk=calendar_id)

    if not request.user.is_superuser and calendar not in request.user.editable_calendars:
        return HttpResponseForbidden('You cannot delete a user from this calendar.')

    user = get_object_or_404(User, username=username)
    calendar.admins.remove(user)
    calendar.editors.remove(user)
    calendar.save()
    return HttpResponseRedirect(reverse('calendar-update', args=(calendar_id,)))

@login_required
def reassign_ownership(request, calendar_id, username):
    calendar = get_object_or_404(Calendar, pk=calendar_id)

    if not request.user.is_superuser and calendar not in request.user.owned_calendars.all():
        return HttpResponseForbidden('You cannot reassign ownership for this calendar.')

    user = get_object_or_404(User, username=username)
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
        if subscribing_calendar not in request.user.calendars:
            return HttpResponseForbidden('You cannot modify the specified calendar.')
        try:
            if calendar not in subscribing_calendar.subscriptions.all():
                subscribing_calendar.subscriptions.add(calendar)
                calendar.copy_future_events(subscribing_calendar)
        except Exception, e:
            log.error(str(e))
            messages.error(request, 'Adding calendar to subscribing list failed.')
        else:
            messages.success(request, 'Calendar successfully subscribed to.')
    return HttpResponseRedirect(reverse('calendar-update', args=(subscribing_calendar_id,)) + '#subscriptions')

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
            calendar.delete_subscribed_events(subscribed_calendar)
        except Exception, e:
            log.error(str(e))
            messages.error(request, 'Removing subscribed calendar failed.')
        else:
            messages.success(request, 'Calendar successfully unsubscribed.')
    return HttpResponseRedirect(reverse('calendar-update', args=(calendar_id,)) + '#subscriptions')
