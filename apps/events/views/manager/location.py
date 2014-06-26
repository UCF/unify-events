import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from core.views import DeleteSuccessMessageMixin
from core.views import SuperUserRequiredMixin
from events.forms.manager import LocationForm
from events.models import Location

log = logging.getLogger(__name__)


class LocationListView(SuperUserRequiredMixin, ListView):
    context_object_name = 'locations'
    model = Location
    paginate_by = 25
    template_name = 'events/manager/location/list.html'

    def get_context_data(self, **kwargs):
        """
        Add review count, state and full location list to context.
        """
        context = super(LocationListView, self).get_context_data(**kwargs)

        context['review_count'] = Location.objects.filter(reviewed=False).count()

        context['state'] = None
        if 'state' in self.kwargs and self.kwargs.get('state'):
            context['state'] = self.kwargs.get('state')

        context['location_list'] = Location.objects.all()

        return context

    def get_queryset(self):
        """
        Filter query to specific location state.
        """
        queryset = super(LocationListView, self).get_queryset()

        state = self.kwargs.get('state')
        if state and state in ['review', 'approved']:
            if state == 'review':
                queryset = queryset.filter(reviewed=False)
            else:
                queryset = queryset.filter(reviewed=True)

        # Append event count to locations.
        queryset = queryset.annotate(event_count=Count('event_instances__event', distinct=True))

        return queryset


class LocationCreateView(SuperUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Location
    template_name = 'events/manager/location/create_update.html'
    form_class = LocationForm
    success_url = reverse_lazy('location-list')
    success_message = '%(title)s was created successfully.'


class LocationUpdateView(SuperUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Location
    template_name = 'events/manager/location/create_update.html'
    form_class = LocationForm
    success_url = reverse_lazy('location-list')
    success_message = '%(title)s was updated successfully.'


class LocationDeleteView(SuperUserRequiredMixin, DeleteSuccessMessageMixin, DeleteView):
    model = Location
    template_name = 'events/manager/location/delete.html'
    success_url = reverse_lazy('location-list')
    success_message = 'Location was deleted successfully.'

    def post(self, request, *args, **kwargs):
        """
        Do not allow the location to be deleted if events
        are assigned to it.
        """
        location = self.get_object()
        if location.event_instances.count() > 0:
            return HttpResponseForbidden('This location has events assigned to it and cannot be deleted.')
        return self.delete(request, *args, **kwargs)


@login_required
def bulk_action(request):
    if request.method == 'POST':
        action_0 = request.POST['bulk-action_0']
        action_1 = request.POST['bulk-action_1']

        if action_0 == action_1 == 'empty':
            messages.error(request, 'No action selected.')
            return HttpResponseRedirect(request.META.HTTP_REFERER)

        action = action_0
        if action == 'empty':
            action = action_1

        if action not in ['approve', 'review', 'delete']:
            messages.error(request, 'Unrecognized action selected %s.' % action)
            return HttpResponseRedirect(request.META.HTTP_REFERER)

        # remove duplicates
        location_ids = request.POST.getlist('object_ids')

        for location_id in location_ids:
            try:
                location = Location.objects.get(pk=location_id)
            except Location.DoesNotExist, e:
                log.error(str(e))
                continue

            if not request.user.is_superuser:
                messages.error(request, 'You do not have permissions to modify Location %s' % location.comboname)
                continue

            if action == 'approve':
                # approve the location
                try:
                    location.reviewed = True
                    location.save()
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to set Location %s to Approved.' % location.comboname)

            elif action == 'review':
                # Set all Locations to Reviewed
                try:
                    location.reviewed = False
                    location.save()
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to set Location %s to Review.' % location.comboname)

            elif action == 'delete':
                # Delete all Locations
                try:
                    location.delete()
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to delete Location %s.' % location.comboname)

        # Determine whether to set a successful message
        error = False
        storage = messages.get_messages(request)
        for message in storage:
            error = True
            storage.used = False
            break

        if not error:
            message = ''
            if action == 'approve':
                message = 'Locations successfully Approved.'
            elif action == 'posted':
                message = 'Locations successfully moved to Review.'
            elif action == 'delete':
                message = 'Locations successfully deleted.'

            messages.success(request, message)

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    raise Http404


@login_required
def merge(request, location_from_id=None, location_to_id=None):
    """
    View for merging the location into another location.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot perform this action.')

    if location_from_id and location_to_id:
        location_from = get_object_or_404(Location, pk=location_from_id)
        location_to = get_object_or_404(Location, pk=location_to_id)

        event_instances = location_from.event_instances.filter(parent=None)
        if event_instances.count() > 0:
            try:
                for event_instance in event_instances:
                    event_instance.location = location_to
                    event_instance.save()
                location_from.delete()
            except Exception, e:
                log.error(str(e))
                messages.error(request, 'Merging location failed.')
            else:
                messages.success(request, 'Location successfully merged.')
        else:
            messages.error(request, 'Cannot merge this location: location has no events. Delete this location instead of merging.')
        return HttpResponseRedirect(reverse('location-list'))

    raise Http404
