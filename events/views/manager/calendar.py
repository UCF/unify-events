from datetime import datetime
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.urls import reverse_lazy
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
from core.views import PaginationRedirectMixin

from settings_local import FRONT_PAGE_CALENDAR_PK
from events.models import Calendar
from events.forms.manager import CalendarForm
from events.forms.manager import CalendarSubscribeForm

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


class CalendarOwnerUserValidationMixin(object):
    """
    Require that the user accessing the calendar is either a superuser
    or owns the calendar.

    Return 403 Forbidden if false.
    """
    def dispatch(self, request, *args, **kwargs):
        if hasattr(super(CalendarOwnerUserValidationMixin, self), 'get_calendar'):
            calendar = self.get_calendar()
        elif hasattr(super(CalendarOwnerUserValidationMixin, self), 'get_object'):
            calendar = self.get_object()
        else:
            calendar = None

        if not self.request.user.is_superuser and calendar is not None and calendar.owner != self.request.user:
            return HttpResponseForbidden('You cannot modify the specified calendar.')
        else:
            return super(CalendarOwnerUserValidationMixin, self).dispatch(request, *args, **kwargs)



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
        self.object.active = True
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


class CalendarDelete(DeleteSuccessMessageMixin, CalendarOwnerUserValidationMixin, DeleteView):
    model = Calendar
    success_message = 'Calendar was successfully deleted.'
    success_url = reverse_lazy('dashboard')
    template_name = 'events/manager/calendar/delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Prevent deletion of the Main Calendar.
        if self.object.is_main_calendar:
            messages.error(self.request, 'This calendar cannot be deleted.')
            return HttpResponseRedirect(reverse_lazy('events.views.manager.calendar-update', kwargs={'pk': self.object.pk}))
        else:
            return super(CalendarDelete, self).delete(self, request, *args, **kwargs)


class CalendarUpdate(SuccessMessageMixin, SuccessUrlReverseKwargsMixin, CalendarAdminUserValidationMixin, UpdateView):
    form_class = CalendarForm
    model = Calendar
    success_message = '%(title)s was updated successfully.'
    template_name = 'events/manager/calendar/update.html'
    success_view_name = 'events.views.manager.calendar-update'
    copy_kwargs = ['pk']

    def post(self, request, *args, **kwargs):
        """
        Prevent updates to the main calendar slug (through editing the title.)

        The main calendar's slug gets cached in the generated root urls.pyc file;
        updating the main calendar slug while the app is running will cause all
        frontend main calendar views to return a 404 until the app is restarted.
        """
        self.object = self.get_object()
        title = self.request.POST.get('title')

        if self.object.is_main_calendar and title and title != self.object.title:
            messages.error(self.request, 'The main calendar title (and its slug) cannot be updated while the application is running.')
            return HttpResponseRedirect(reverse_lazy('events.views.manager.calendar-update', kwargs={'pk': self.object.pk}))
        else:
            return super(CalendarUpdate, self).post(self, request, *args, **kwargs)



class CalendarUserUpdate(CalendarAdminUserValidationMixin, DetailView):
    model = Calendar
    success_message = 'Calendar users updated successfully.'
    template_name = 'events/manager/calendar/update/update-users.html'

    def get_context_data(self, **kwargs):
        """
        Get additional context data.
        """
        context = super(CalendarUserUpdate, self).get_context_data(**kwargs)

        ctx = {
            'users': User.objects.all().order_by('last_name', 'first_name')
        }
        ctx.update(context)

        return ctx


class CalendarSubscriptionsUpdate(CalendarAdminUserValidationMixin, DetailView):
    model = Calendar
    template_name = 'events/manager/calendar/update/update-subscriptions.html'


class CalendarList(SuperUserRequiredMixin, PaginationRedirectMixin, ListView):
    context_object_name = 'calendars'
    model = Calendar
    paginate_by = 25
    template_name = 'events/manager/calendar/list.html'


@login_required
def add_update_user(request, pk, username, role):
    calendar = get_object_or_404(Calendar, pk=pk)

    if not request.user.is_superuser and calendar not in request.user.editable_calendars:
        return HttpResponseForbidden('You cannot add/update users to the specified calendar.')

    # Try to use GET params, if they're available.
    if not username or not User.objects.filter(username=username).exists() or username == 'username':
        user = get_object_or_404(User, username=request.GET.get('username_d'))
    else:
        user = get_object_or_404(User, username=username)

    get_role = request.GET.get('role', None)
    get_role = get_role if get_role in ['admin', 'editor'] else None
    role = role if role in ['admin', 'editor'] else None
    if role is None and get_role is not None:
        role = get_role

    # Update user...
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
    url_name = 'events.views.manager.calendar-update-users'
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
        return HttpResponseRedirect(reverse('events.views.manager.calendar-update-users', args=(pk,)))

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
    return HttpResponseRedirect(reverse('events.views.manager.calendar-update-users', args=(pk,)))


class SubscribeToCalendar(SuccessMessageMixin, UpdateView):
    model = Calendar
    form_class = CalendarSubscribeForm
    success_message = 'Calendar subscribed to successfully.'
    success_url = reverse_lazy('dashboard')
    template_name = 'events/manager/calendar/update/add-subscription.html'

    def get_form_kwargs(self):
        """
        Get additional context data for the form.
        """
        kwargs = super(SubscribeToCalendar, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """
        Intercept default save of self.get_object(); save instead to
        each selected calendar(s)' subscriptions val.

        Catch invalid calendar requests here.
        """
        original_calendar = self.get_object()
        subscribing_calendars = form.cleaned_data['calendars']

        for calendar in subscribing_calendars:
            if not self.request.user.is_superuser and calendar not in self.request.user.editable_calendars:
                messages.error(self.request, 'You cannot modify subscriptions for the calendar %s.' % calendar.title)
            else:
                try:
                    if original_calendar not in calendar.subscriptions.all():
                        calendar.subscriptions.add(original_calendar)
                        original_calendar.copy_future_events(calendar)
                except Exception as e:
                    log.error(str(e))
                    messages.error(self.request, 'Could not subscribe your calendar %s to %s.' % (calendar.title, original_calendar.title))
                else:
                    messages.success(self.request, '%s was successfully subscribed to %s.' % (calendar.title, original_calendar.title))

        return HttpResponseRedirect(self.get_success_url())


    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        messages.error(self.request, 'Something wasn\'t entered correctly. Please review the errors below and try again.')
        return super(SubscribeToCalendar, self).form_invalid(form)



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
        except Exception as e:
            log.error(str(e))
            messages.error(request, 'Removing subscribed calendar failed.')
        else:
            messages.success(request, 'Calendar successfully unsubscribed.')
    return HttpResponseRedirect(reverse('events.views.manager.calendar-update-subscriptions', args=(pk,)) + '#subscriptions')
