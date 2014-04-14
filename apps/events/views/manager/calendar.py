from datetime import datetime
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from core.views import SuccessUrlReverseKwargsMixin
from core.views import FirstLoginTemplateMixin
from core.views import SuperUserRequiredMixin
from core.views import DeleteSuccessMessageMixin

from settings_local import FRONT_PAGE_CALENDAR_PK
from events.models import Calendar
from events.forms.manager import CalendarForm

log = logging.getLogger(__name__)


class CalendarUserValidationMixin(object):
    """
    Require that the user accessing the calendar is either a superuser
    or is a user assigned to the calendar.

    Return 403 Forbidden if false.
    """
    def dispatch(self, request, *args, **kwargs):
        if hasattr(super(CalendarUserValidationMixin, self), 'get_calendar'):
            calendar = self.get_calendar()
        elif hasattr(super(CalendarUserValidationMixin, self), 'get_object'):
            calendar = self.get_object()
        else:
            calendar = None

        if not self.request.user.is_superuser and calendar is not None and calendar not in self.request.user.calendars.all():
            return HttpResponseForbidden('You cannot modify the specified calendar.')
        else:
            return super(CalendarUserValidationMixin, self).dispatch(request, *args, **kwargs)


class CalendarAdminUserValidationMixin(object):
    """
    Require that the user accessing the calendar is either a superuser
    or is capable of editing the calendar.

    Return 403 Forbidden if false.
    """
    def dispatch(self, request, *args, **kwargs):
        if hasattr(super(CalendarAdminUserValidationMixin, self), 'get_calendar'):
            calendar = self.get_calendar()
        elif hasattr(super(CalendarAdminUserValidationMixin, self), 'get_object'):
            calendar = self.get_object()
        else:
            calendar = None

        if not self.request.user.is_superuser and calendar is not None and calendar not in self.request.user.editable_calendars.all():
            return HttpResponseForbidden('You cannot modify the specified calendar.')
        else:
            return super(CalendarAdminUserValidationMixin, self).dispatch(request, *args, **kwargs)



class CalendarCreate(FirstLoginTemplateMixin, SuccessMessageMixin, CreateView):
    form_class = CalendarForm
    model = Calendar
    success_message = '%(title)s was created successfully.'
    success_url = reverse_lazy('dashboard')
    template_name = 'events/manager/calendar/create.html'
    first_login_template_name = 'events/manager/firstlogin/calendar_create.html'

    def form_valid(self, form):
        """
        Set the calendar owner when validating the form.
        """
        self.object = form.save()
        self.object.owner = self.request.user
        title = form.cleaned_data['title']
        main_title = Calendar.objects.get(pk=FRONT_PAGE_CALENDAR_PK).title

        if title.lower() == main_title.lower():
            messages.error(self.request, 'A calendar with this title cannot be created. Please use a different calendar title and try again.')
            return super(CalendarCreate, self).form_invalid(form)
        else:
            return super(CalendarCreate, self).form_valid(form)

    def render_to_response(self, context, **response_kwargs):
        """
        Force User.first_login to be false so that the next request to the
        Dashboard or Settings does not loop back through the "First Login" check
        """
        template = self.get_template_names()
        self.request.user.last_login = datetime.now()
        self.request.user.save()

        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request = self.request,
            template = template,
            context = context,
            **response_kwargs
        )


class CalendarDelete(DeleteSuccessMessageMixin, CalendarAdminUserValidationMixin, DeleteView):
    model = Calendar
    success_message = 'Calendar was successfully deleted.'
    success_url = reverse_lazy('dashboard')
    template_name = 'events/manager/calendar/delete.html'


class CalendarUpdate(SuccessMessageMixin, SuccessUrlReverseKwargsMixin, CalendarAdminUserValidationMixin, UpdateView):
    form_class = CalendarForm
    model = Calendar
    success_message = '%(title)s was updated successfully.'
    template_name = 'events/manager/calendar/update.html'
    success_view_name = 'calendar-update'
    copy_kwargs = ['pk']


class CalendarUserUpdate(CalendarAdminUserValidationMixin, DetailView):
    model = Calendar
    success_message = 'Calendar users updated successfully.'
    template_name = 'events/manager/calendar/update/update-users.html'


class CalendarSubscriptionsUpdate(CalendarAdminUserValidationMixin, DetailView):
    model = Calendar
    template_name = 'events/manager/calendar/update/update-subscriptions.html'


class CalendarList(SuperUserRequiredMixin, ListView):
    context_object_name = 'calendars'
    model = Calendar
    paginate_by = 25
    template_name = 'events/manager/calendar/list.html'


@login_required
def add_update_user(request, pk, username, role):
    calendar = get_object_or_404(Calendar, pk=pk)

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
    url_name = 'calendar-update-users'
    if request.user == user and role == 'editor' and not request.user.is_superuser:
        url_name = 'dashboard'

    return HttpResponseRedirect(reverse(url_name, kwargs={'pk': pk}))

@login_required
def delete_user(request, pk, username):
    calendar = get_object_or_404(Calendar, pk=pk)

    if not request.user.is_superuser and calendar not in request.user.editable_calendars:
        return HttpResponseForbidden('You cannot delete a user from this calendar.')

    user = get_object_or_404(User, username=username)
    calendar.admins.remove(user)
    calendar.editors.remove(user)
    calendar.save()

    if request.user == user:
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return HttpResponseRedirect(reverse('calendar-update-users', args=(pk,)))

@login_required
def reassign_ownership(request, pk, username):
    calendar = get_object_or_404(Calendar, pk=pk)

    if not request.user.is_superuser and calendar not in request.user.owned_calendars.all():
        return HttpResponseForbidden('You cannot reassign ownership for this calendar.')

    user = get_object_or_404(User, username=username)
    calendar.admins.add(calendar.owner)
    calendar.owner = user
    calendar.admins.remove(user)
    calendar.editors.remove(user)
    calendar.save()
    return HttpResponseRedirect(reverse('calendar-update-users', args=(pk,)))

@login_required
def subscribe_to_calendar(request, pk=None, subscribing_calendar_id=None):
    try:
        calendar = Calendar.objects.get(pk=pk)
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
    return HttpResponseRedirect(reverse('calendar-update-subscriptions', args=(subscribing_calendar_id,)) + '#subscriptions')

@login_required
def unsubscribe_from_calendar(request, pk=None, subscribed_calendar_id=None):
    try:
        calendar = Calendar.objects.get(pk=pk)
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
    return HttpResponseRedirect(reverse('calendar-update-subscriptions', args=(pk,)) + '#subscriptions')
