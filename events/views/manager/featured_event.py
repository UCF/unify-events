from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.urls import reverse_lazy
from core.views import PaginationRedirectMixin, SuperUserRequiredMixin

from events.forms.manager import FeaturedEventForm
from events.models import FeaturedEvent

class FeaturedEventListView(SuperUserRequiredMixin, PaginationRedirectMixin, ListView):
    model = FeaturedEvent
    context_object_name = 'featured_events'
    paginate_by = 25
    template_name = 'events/manager/featured_event/list.html'
    success_url = reverse_lazy('events.views.manager.featured_event.list')

class FeaturedEventCreateView(CreateView):
    model = FeaturedEvent
    form_class = FeaturedEventForm
    prefix = 'featured_event'
    template_name = 'events/manager/featured_event/create.html'
    success_url = reverse_lazy('events.views.manager.featured_event.list')

class FeaturedEventUpdateView(UpdateView):
    model = FeaturedEvent
    form_class = FeaturedEventForm
    prefix = 'featured_event'
    template_name = 'events/manager/featured_event/update.html'
    success_url = reverse_lazy('events.views.manager.featured_event.list')

class FeaturedEventDeleteView(DeleteView):
    model = FeaturedEvent
    template_name = 'events/manager/featured_event/delete.html'
    prefix = 'featured_event'
    success_url = reverse_lazy('events.views.manager.featured_event.list')
