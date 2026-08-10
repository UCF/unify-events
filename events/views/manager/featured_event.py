from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.urls import reverse_lazy

from core.views import PaginationRedirectMixin, SuperUserRequiredMixin

from events.forms.manager import FeaturedEventForm
from events.models import FeaturedEvent


# SuperUserRequiredMixin goes first on every view here so that its dispatch()
# runs before the generic view's. Featuring an event puts artwork on the
# calendar home page, so write access has to be gated as tightly as read.

class FeaturedEventListView(SuperUserRequiredMixin, PaginationRedirectMixin, ListView):
    model = FeaturedEvent
    context_object_name = 'featured_events'
    paginate_by = 25
    template_name = 'events/manager/featured_event/list.html'
    success_url = reverse_lazy('events.views.manager.featured_event.list')

    def get_context_data(self, **kwargs):
        """
        Several entries can be eligible at once, but only one displays. Pass
        that one through so the list can say which.
        """
        context = super(FeaturedEventListView, self).get_context_data(**kwargs)
        context['active_featured_event'] = FeaturedEvent.objects.get_active()
        return context


class FeaturedEventCreateView(SuperUserRequiredMixin, CreateView):
    model = FeaturedEvent
    form_class = FeaturedEventForm
    context_object_name = 'featured_event'
    template_name = 'events/manager/featured_event/create.html'
    success_url = reverse_lazy('events.views.manager.featured_event.list')


class FeaturedEventUpdateView(SuperUserRequiredMixin, UpdateView):
    model = FeaturedEvent
    form_class = FeaturedEventForm
    context_object_name = 'featured_event'
    template_name = 'events/manager/featured_event/update.html'
    success_url = reverse_lazy('events.views.manager.featured_event.list')


class FeaturedEventDeleteView(SuperUserRequiredMixin, DeleteView):
    model = FeaturedEvent
    context_object_name = 'featured_event'
    template_name = 'events/manager/featured_event/delete.html'
    success_url = reverse_lazy('events.views.manager.featured_event.list')
