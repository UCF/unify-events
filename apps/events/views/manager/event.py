import logging

from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from core.forms import RequiredModelFormSet
from core.views import DeleteSuccessMessageMixin
from events.forms.manager import EventCopyForm
from events.forms.manager import EventForm
from events.forms.manager import EventInstanceForm
from events.forms.manager import EventInstanceFormSet
from events.models import get_main_calendar
from events.models import Event
from events.models import EventInstance
from events.models import Location
from events.models import State
from taggit.models import Tag

log = logging.getLogger(__name__)


class EventCreate(CreateView):
    model = Event
    form_class = EventForm
    prefix = 'event'
    template_name = 'events/manager/events/create_update.html'
    success_url = '/manager/'

    def get_initial(self):
        """
        Set the set of calendars the user can select from
        """
        initial = super(EventCreate, self).get_initial()
        initial['user_calendars'] = self.request.user.calendars
        return initial

    def get_context_data(self, **kwargs):
        """
        Get additional context data.
        """
        context = super(EventCreate, self).get_context_data(**kwargs)

        ctx = {
               'locations': Location.objects.all(),
               'tags': Tag.objects.all()
        }
        ctx.update(context)

        return ctx

    def get(self, request, *args, **kwargs):
        """
        Handles the GET request and instantiates blank versions
        of the form and inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        event_instance_formset = EventInstanceFormSet()
        return self.render_to_response(self.get_context_data(form=form,
                                                             event_instance_formset=event_instance_formset))

    def post(self, request, *args, **kwargs):
        """
        Checks the form and formset validity and user permissions on
        the calendar the event will be created for.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        event_instance_formset = EventInstanceFormSet(self.request.POST)
        if form.is_valid() and event_instance_formset.is_valid():
            # Can user add an event to this calendar?
            if not self.request.user.is_superuser and form.instance.calendar not in self.request.user.calendars:
                return HttpResponseForbidden('You cannot add an event to this calendar.')

            return self.form_valid(form, event_instance_formset)
        else:
            return self.form_invalid(form, event_instance_formset)

    def form_valid(self, form, event_instance_formset):
        """
        Called if all forms are valid. Sets event creator.
        Creates an event instance and redirects to success url.
        """
        form.instance.creator = self.request.user
        self.object = form.save()
        event_instance_formset.instance = self.object
        event_instance_formset.save()

        # Import to main calendar if requested
        if form.cleaned_data['submit_to_main']:
            get_main_calendar().import_event(self.object)

        # Copy event for subscribed calendars
        for subscribed_calendar in self.object.calendar.subscribed_calendars.all():
            subscribed_calendar.import_event(self.object)

        messages.success(self.request, 'Event successfully saved')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, event_instance_formset):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        messages.error(self.request, 'Something wasn\'t entered correctly. Please review the errors below and try again.')
        return self.render_to_response(
            self.get_context_data(form=form,
                                  event_instance_formset=event_instance_formset))


class EventUpdate(UpdateView):
    model = Event
    form_class = EventForm
    prefix = 'event'
    template_name = 'events/manager/events/create_update.html'
    success_url = '/manager/'

    def get_initial(self):
        """
        Set the set of calendars the user can select from
        """
        initial = super(EventUpdate, self).get_initial()
        initial['user_calendars'] = self.request.user.calendars
        return initial

    def get_context_data(self, **kwargs):
        """
        Get additional context data.
        """
        context = super(EventUpdate, self).get_context_data(**kwargs)

        ctx = {
               'locations': Location.objects.all(),
               'tags': Tag.objects.all(),
               # Needed to determine whether to show the cancel/un-cancel button
               'posted_state': State.posted
        }
        ctx.update(context)

        return ctx

    def get(self, request, *args, **kwargs):
        """
        Handles the GET request and instantiates the object for
        the form and inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        # Can user add an event to this calendar?
        if not self.request.user.is_superuser and form.instance.calendar not in self.request.user.calendars:
            return HttpResponseForbidden('You cannot modify the specified event.')

        # Remove extra form and set related object to get all event instances
        EventInstanceFormSet.extra = 0
        event_instance_formset = EventInstanceFormSet(instance=self.object,
                                                      queryset=self.object.event_instances.filter(parent=None))
        return self.render_to_response(self.get_context_data(form=form,
                                                             event_instance_formset=event_instance_formset))

    def post(self, request, *args, **kwargs):
        """
        Checks the form and formset validity and user permissions on
        the calendar the event will be created for.
        """

        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        # Can user add an event to this calendar?
        if not self.request.user.is_superuser and form.instance.calendar not in self.request.user.calendars:
            return HttpResponseForbidden('You cannot add an event to this calendar.')

        event_instance_formset = EventInstanceFormSet(data=self.request.POST,
                                                      instance=self.object)
        if form.is_valid() and event_instance_formset.is_valid():
            return self.form_valid(form, event_instance_formset)
        else:
            return self.form_invalid(form, event_instance_formset)

    def form_valid(self, form, event_instance_formset):
        """
        Called if all forms are valid. Creates an event instance
        and redirects to success url.
        """
        form.instance.creator = self.request.user

        self.object = form.save()
        event_instance_formset.save()

        # Check if main calendar submission should be re-reviewed
        is_main_rereview = False
        if any(s in form.changed_data for s in ['description', 'title']):
            is_main_rereview = True

        # Updates the copied versions if the original event is updated
        for copied_event in self.object.duplicated_to.all():
            copy = copied_event.pull_updates(is_main_rereview)

        # Import to main calendar if requested and is NOT already submitted to main calendar
        if not self.object.is_submit_to_main and form.cleaned_data['submit_to_main']:
            get_main_calendar().import_event(self.object)

        messages.success(self.request, 'Event successfully saved')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, event_instance_formset):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        messages.error(self.request, 'Something wasn\'t entered correctly. Please review the errors below and try again.')
        return self.render_to_response(
            self.get_context_data(form=form,
                                  event_instance_formset=event_instance_formset))


class EventDelete(DeleteSuccessMessageMixin, DeleteView):
    model = Event
    template_name = 'events/manager/events/delete.html'
    success_url = '/manager/'
    success_message = 'Event was successfully deleted.'

    def delete(self, request, *args, **kwargs):
        """
        Ensure the user has the permissions to delete the event
        """
        if not self.request.user.is_superuser and self.get_object().calendar not in self.request.user.calendars:
            return HttpResponseForbidden('You cannot delete the specified event.')

        return super(EventDelete, self).delete(request, *args, **kwargs)


@login_required
def update_state(request, pk=None, state=None):
    event = get_object_or_404(Event, pk=pk)

    if not request.user.is_superuser and event.calendar not in request.user.calendars:
        return HttpResponseForbidden('You cannot modify the state for the specified event.')

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
def submit_to_main(request, pk=None):
    event = get_object_or_404(Event, pk=pk)

    if not request.user.is_superuser and event.calendar not in request.user.calendars:
        return HttpResponseForbidden('You cannot modify the specified event.')

    if not event.is_submit_to_main:
        get_main_calendar().import_event(event)
    try:
        event.save()
    except Exception, e:
        log.error(str(e))
        messages.error(request, 'Saving event failed.')
    else:
        messages.success(request, 'Event successfully updated.')

    return HttpResponseRedirect(reverse('dashboard', kwargs={'calendar_id': event.calendar.id}))


@login_required
def bulk_action(request):
    if request.method == 'POST':
        action_0 = request.POST['bulk-action_0']
        action_1 = request.POST['bulk-action_1']

        if action_0 == action_1 == 'Select Action...':
            messages.error(request, 'No action selected.')
            return HttpResponseRedirect(request.META.HTTP_REFERER)

        action = action_0
        if action == 'Select Action...':
            action = action_1

        if action not in ['submit-to-main', 'posted', 'pending', 'delete']:
            messages.error(request, 'Unrecognized action selected %s.' % action)
            return HttpResponseRedirect(request.META.HTTP_REFERER)

        # remove duplicates
        event_ids = list(set(request.POST.getlist('event_ids', [])))

        for event_id in event_ids:
            try:
                event = Event.objects.get(pk=event_id)
            except Event.DoesNotExist, e:
                # The subscription event may not exist anymore since
                # the original event has been deleted, thus deleting
                # the subscription events. Log and fail gracefully.
                log.error(str(e))
                continue

            if not request.user.is_superuser and event.calendar not in request.user.calendars:
                messages.error(request, 'You do not have permissions to modify Event %s' % event.title)
                continue

            if action == 'submit-to-main' and not event.is_submit_to_main:
                # Submit all Events to Main Calendar
                try:
                    get_main_calendar().import_event(event)
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to submit Event %s to the Main Calendar.' % event.title)

            elif action == 'posted':
                # Set all Events to Posted
                try:
                    event.state = State.posted
                    event.save()
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to set Event %s to Posted.' % event.title)

            elif action == 'pending':
                # Set all Events to Pending
                try:
                    event.state = State.pending
                    event.save()
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to move Event %s to Pending.' % event.title)

            elif action == 'delete':
                # Delete all Events
                try:
                    event.delete()
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to delete Event %s.' % event.title)

        # Determine whether to set a successful message
        error = False
        storage = messages.get_messages(request)
        for message in storage:
            error = True
            storage.used = False
            break

        if not error:
            message = ''
            if action == 'submit-to-main':
                message = 'Events successfully submitted to the Main Calendar.'
            elif action == 'posted':
                message = 'Events successfully added to Posted.'
            elif action == 'pending':
                message = 'Events successfully moved to Pending.'
            elif action == 'delete':
                message = 'Events successfully deleted.'

            messages.success(request, message)

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    raise Http404


@login_required
def cancel_uncancel(request, pk=None):
    event = get_object_or_404(Event, pk=pk)

    # Get original event
    original_event = event
    if event.created_from:
        event = event.created_from

    if not request.user.is_superuser and event.calendar not in request.user.calendars:
        return HttpResponseForbidden('You cannot modify the specified event.')

    try:
        event.canceled = not event.canceled
        event.save()

        # Updates the copied versions if the original event is updated
        for copied_event in event.duplicated_to.all():
            copy = copied_event.pull_updates()

    except Exception, e:
        log.error(str(e))
        messages.error(request, 'Canceling/Un-Canceling event failed.')
    else:
        message = 'Event successfully un-canceled.'
        if event.canceled:
            message = 'Event successfully canceled.'

        messages.success(request, message)
    return HttpResponseRedirect(reverse('dashboard', kwargs={'calendar_id': original_event.calendar.id}))


@login_required
def copy(request, event_id=None):
    ctx = {'event': None, 'form': None}
    tmpl = 'events/manager/events/copy.html'

    ctx['event'] = get_object_or_404(Event, pk=event_id)

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
                except Exception:
                    messages.error(request, 'Unable to copy even to %s' % calendar.title)
                    error = True
            if not error:
                messages.success(request, 'Event successfully copied.')
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        ctx['form'] = EventCopyForm(calendars=user_calendars)
    return TemplateView.as_view(request, tmpl, ctx)
