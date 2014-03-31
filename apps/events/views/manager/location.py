import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.generic import DetailView
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
        Add review count and state to context.
        """
        context = super(LocationListView, self).get_context_data(**kwargs)

        context['review_count'] = Location.objects.filter(reviewed=False).count()

        context['state'] = None
        if 'state' in self.kwargs and self.kwargs.get('state'):
            context['state'] = self.kwargs.get('state')

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
    success_message = '%(title)s was deleted successfully.'


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

        if action not in ['approve', 'review', 'delete']:
            messages.error(request, 'Unrecognized action selected %s.' % action)
            return HttpResponseRedirect(request.META.HTTP_REFERER)

        # remove duplicates
        location_ids = request.POST.getlist('location_ids')

        for location_id in location_ids:
            try:
                location = Location.objects.get(pk=location_id)
            except Location.DoesNotExist, e:
                log.error(str(e))
                continue

            if not request.user.is_superuser:
                messages.error(request, 'You do not have permissions to modify Location %s' % location.title)
                continue

            if action == 'approve':
                # approve the location
                try:
                    location.reviewed = True
                    location.save()
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to set Location %s to Approved.' % location.title)

            elif action == 'review':
                # Set all Locations to Reviewed
                try:
                    location.reviewed = False
                    location.save()
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to set Location %s to Review.' % location.title)

            elif action == 'delete':
                # Delete all Locations
                try:
                    location.delete()
                except Exception, e:
                    log.error(str(e))
                    messages.error(request, 'Unable to delete Location %s.' % location.title)

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
