import logging
import urllib

from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from core.forms import RequiredModelFormSet
from core.views import DeleteSuccessMessageMixin
from core.views import SuccessPreviousViewRedirectMixin
from core.views import success_previous_view_redirect
from events.forms.manager import EventCopyForm
from events.forms.manager import EventForm
from events.forms.manager import EventInstanceForm
from events.forms.manager import EventInstanceCreateFormSet
from events.forms.manager import EventInstanceUpdateFormSet
from events.functions import update_subscriptions
from events.models import get_main_calendar
from events.models import Calendar
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
    success_url = reverse_lazy('dashboard')

    def get_initial(self):
        """
        Set the set of calendars the user can select from
        """
        initial = super(EventCreate, self).get_initial()
        if self.request.user.is_superuser:
            initial['user_calendars'] = Calendar.objects.all()
        else:
            initial['user_calendars'] = self.request.user.calendars
        return initial

    def get_context_data(self, **kwargs):
        """
        Get additional context data.
        """
        context = super(EventCreate, self).get_context_data(**kwargs)
        ctx = {
               'locations': Location.objects.all(),
               'tags': Tag.objects.all().order_by('name')
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

        event = Event()
        event_instance_formset = EventInstanceCreateFormSet(instance=event)

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

        if form.is_valid():
            # Can user add an event to this calendar?
            if not self.request.user.is_superuser and form.instance.calendar not in self.request.user.calendars:
                return HttpResponseForbidden('You cannot add an event to this calendar.')

            event = form.save(commit=False)
            event_instance_formset = EventInstanceCreateFormSet(
                data=self.request.POST,
                instance=event
            )

            if event_instance_formset.is_valid():
                return self.form_valid(form, event_instance_formset)
            else:
                return self.form_invalid(form, event_instance_formset)
        else:
            event = Event()
            event_instance_formset = EventInstanceCreateFormSet(
                data=self.request.POST,
                instance=event
            )
            return self.form_invalid(form, event_instance_formset)

    def form_valid(self, form, event_instance_formset):
        """
        Called if all forms are valid. Sets event creator.
        Creates an event instance and redirects to success url.
        """
        form.instance.creator = self.request.user
        try:
            self.object = form.save()
            event_instance_formset.save()
        except Exception, e:
            """
            Try to catch errors gracefully here, but make sure they're logged
            """
            log.error(str(e))
            messages.error(self.request,
                           'Something went wrong while trying to create this \
                           event. Please try again.')
            return self.render_to_response(
                self.get_context_data(form=form,
                                      event_instance_formset=event_instance_formset))
        else:
            # Import to main calendar if requested and state is posted
            if form.cleaned_data['submit_to_main']:
                if self.object.state == State.posted:
                    get_main_calendar().import_event(self.object)
                    messages.success(self.request, 'Event successfully submitted to the Main Calendar. Please allow 2-3 days for your event to be reviewed before it is posted to UCF\'s Main Calendar.')
                else:
                    messages.error(self.request, 'Event can not be submitted to the Main Calendar unless it is posted on your calendar.')

            update_subscriptions(self.object)

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


class EventUpdate(SuccessPreviousViewRedirectMixin, UpdateView):
    model = Event
    form_class = EventForm
    prefix = 'event'
    template_name = 'events/manager/events/create_update.html'
    success_url = reverse_lazy('dashboard')

    def get_initial(self):
        """
        Set the set of calendars the user can select from
        """
        initial = super(EventUpdate, self).get_initial()
        if self.request.user.is_superuser:
            initial['user_calendars'] = Calendar.objects.all()
        else:
            initial['user_calendars'] = self.request.user.calendars
        return initial

    def get_context_data(self, **kwargs):
        """
        Get additional context data.
        """
        context = super(EventUpdate, self).get_context_data(**kwargs)

        ctx = {
               'locations': Location.objects.all(), # Always pass all locations here so that users can modify events with locations that are in review
               'tags': Tag.objects.all().order_by('name'),
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
        event_instance_formset = EventInstanceUpdateFormSet(instance=self.object,
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

        event_instance_formset = EventInstanceUpdateFormSet(data=self.request.POST,
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
        try:
            self.object = form.save()
            event_instance_formset.save()
        except Exception, e:
            """
            Try to catch errors gracefully here, but make sure they're logged
            """
            log.error(str(e))
            messages.error(self.request,
                           'Something went wrong while trying to save this \
                           event. Please try again.')
            return self.render_to_response(
                self.get_context_data(form=form,
                                      event_instance_formset=event_instance_formset))
        else:
            # Check if main calendar submission should be re-reviewed
            is_main_rereview = False
            if any(s in form.changed_data for s in ['description', 'title']):
                is_main_rereview = True

            # Import to main calendar if posted, is requested and
            # is NOT already submitted to main calendar
            if not self.object.is_submit_to_main and form.cleaned_data['submit_to_main']:
                if self.object.state == State.posted:
                    get_main_calendar().import_event(self.object)
                    messages.success(self.request, 'Event successfully submitted to the Main Calendar. Please allow 2-3 days for your event to be reviewed before it is posted to UCF\'s Main Calendar.')
                else:
                    messages.error(self.request, 'Event can not be submitted to the Main Calendar unless it is posted on your calendar.')
            elif self.object.is_submit_to_main and self.object.state != State.posted and not self.object.calendar.is_main_calendar:
                messages.info(self.request, 'Event was removed from the Main Calendar since the event is not posted on your calendar.')

            update_subscriptions(self.object, is_main_rereview)

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


class EventDelete(SuccessPreviousViewRedirectMixin, DeleteSuccessMessageMixin, DeleteView):
    model = Event
    template_name = 'events/manager/events/delete.html'
    success_url = reverse_lazy('dashboard')
    success_message = 'Event was successfully deleted.'

    def get_context_data(self, **kwargs):
        """
        Override form_action_next added from SuccessPreviousViewRedirectMixin
        if the previous view is the Event Update view (redirecting to this view
        on a successful delete will return a 404.)
        """
        context = super(EventDelete, self).get_context_data(**kwargs)
        form_action_next = context.get('form_action_next', None)

        if form_action_next:
            next = urllib.unquote_plus(form_action_next)
            next_relative = self.get_relative_path_with_query(next)
            try:
                view, v_args, v_kwargs = resolve(next_relative.path)
            except Http404:
                pass
            else:
                if view.__name__ == 'EventUpdate':
                    ctx = {
                        'form_action_next': urllib.quote_plus(reverse(
                                'dashboard-calendar-state',
                            kwargs = {
                                'pk': self.object.calendar.pk,
                                'state': State.get_string(self.object.state)
                            }
                        ))
                    }
                    context.update(ctx)

        return context

    def delete(self, request, *args, **kwargs):
        """
        Ensure the user has the permissions to delete the event
        """
        if not self.request.user.is_superuser and self.get_object().calendar not in self.request.user.calendars:
            return HttpResponseForbidden('You cannot delete the specified event.')

        return super(EventDelete, self).delete(request, *args, **kwargs)


def update_event_state(request, pk=None, state=None):
    """
    Update the state of the event.
    """
    event = get_object_or_404(Event, pk=pk)

    if not request.user.is_superuser and event.calendar not in request.user.calendars:
        messages.error(request, 'You cannot modify the state for Event %s.' % event.title)
    else:
        event.state = state
        try:
            event.save()
        except Exception, e:
            log(str(e))
            messages.error(request, 'Unable to set Event %(1)s to %(2)s.' % {"1": event.title, "2": State.get_string(state)})
        else:
            if event.is_submit_to_main and event.state != State.posted and not event.calendar.is_main_calendar:
                messages.info(request, 'Event %s was removed from the Main Calendar since the event is not posted on your calendar.' % event.title)

            update_subscriptions(event)

            messages.success(request, 'Successfully updated Event %(1)s to %(2)s.' % {"1": event.title, "2": State.get_string(state)})

    return event


def submit_event_to_main(request, pk=None):
    """
    Submit the event to the main calendar.
    """
    event = get_object_or_404(Event, pk=pk)

    if not request.user.is_superuser and event.calendar not in request.user.calendars:
        messages.error(request, 'You cannot submit Event %s to the Main Calendar.' % event.title)
    else:
        if event.state == State.posted:
            if not event.is_submit_to_main:
                try:
                    get_main_calendar().import_event(event)
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to submit Event %s to the Main Calendar.' % event.title)
                else:
                    messages.success(request, 'Event %s was successfully submitted to the Main Calendar. Please allow 2-3 days for your event to be reviewed before it is posted to UCF\'s Main Calendar.' % event.title)
            else:
                messages.warning(request, 'Event %s has already been submitted to the Main Calendar. Please allow 2-3 days for your event to be reviewed before it is posted to UCF\'s Main Calendar.' % event.title)
        else:
            messages.error(request, 'Event %s can not be submitted to the Main Calendar unless it is posted on your calendar.' % event.title)

    return event


@login_required
def update_state(request, pk=None, state=None):
    """
    View to update the state of the event.
    """
    event = update_event_state(request, pk, state)
    return success_previous_view_redirect(request, reverse('dashboard', kwargs={'pk': event.calendar.id}))


@login_required
def submit_to_main(request, pk=None):
    """
    View to submit the event to the main calendar.
    """
    event = submit_event_to_main(request, pk)
    return success_previous_view_redirect(request, reverse('dashboard', kwargs={'pk': event.calendar.id}))


@login_required
def bulk_action(request):
    if request.method == 'POST':
        action_0 = request.POST['bulk-action_0']
        action_1 = request.POST['bulk-action_1']

        if action_0 == action_1 == 'empty':
            messages.error(request, 'No action selected.')
            return success_previous_view_redirect(request, reverse('dashboard'))

        action = action_0
        if action == 'empty':
            action = action_1

        if action not in ['submit-to-main', 'posted', 'pending', 'delete']:
            messages.error(request, 'Unrecognized action selected %s.' % action)
            return success_previous_view_redirect(request, reverse('dashboard'))

        # remove duplicates
        event_ids = list(set(request.POST.getlist('object_ids', [])))

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

            if action == 'submit-to-main':
                submit_event_to_main(request, event_id)

            elif action == 'posted':
                update_event_state(request, event_id, State.posted)

            elif action == 'pending':
                update_event_state(request, event_id, State.pending)

            elif action == 'delete':
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

        return success_previous_view_redirect(request, reverse('dashboard'))
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
    return success_previous_view_redirect(request, reverse('dashboard', kwargs={'pk': original_event.calendar.id}))


@login_required
def copy(request, pk=None):
    tmpl = 'events/manager/events/copy.html'

    event = get_object_or_404(Event, pk=pk)
    user_calendars = request.user.calendars.exclude(pk=event.calendar.id)

    if request.method == 'POST':
        form = EventCopyForm(request.POST, calendars=user_calendars)
        if form.is_valid():
            for calendar in form.cleaned_data['calendars']:
                error = False
                if not request.user.is_superuser and calendar not in request.user.calendars:
                    messages.error(request, 'You cannot copy the specified event to the calendar %s.' % calendar.title)
                    error = True
                else:
                    try:
                        # Check against both the current event's pk and its original, if it exists.
                        # Prevents copies more than one level deep.
                        if event.created_from:
                            created_from = event.created_from.pk
                        else:
                            created_from = event.pk
                        original_event_pks = list(set([event.pk, created_from]))

                        pk = Q(pk__in=original_event_pks)
                        created_from = Q(created_from__in=original_event_pks)
                        _filter = pk | created_from

                        existing_event = Event.objects.get(_filter, calendar=calendar.pk)

                        if existing_event:
                            messages.error(request, 'This event already exists on the calendar %s and was skipped.' % calendar.title)
                            error = True
                    except Event.DoesNotExist:
                        try:
                            event.copy(calendar=calendar)
                        except Exception:
                            messages.error(request, 'Unable to copy event to %s' % calendar.title)
                            error = True
                if not error:
                    messages.success(request, 'Event successfully copied to calendar %s.' % calendar.title)
            return HttpResponseRedirect(reverse('dashboard-state', kwargs={'state': 'subscribed'}))
        else:
            messages.error(request, 'Something went wrong when trying to copy to one of the selected calendars. Please try again.')
            error = True
            return HttpResponseRedirect(reverse('event-copy', kwargs={'pk': event.id}))
    else:
        form = EventCopyForm(calendars=user_calendars)
    view = TemplateView.as_view(template_name=tmpl)
    return view(request, event=event, form=form)
