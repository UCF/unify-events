from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.urls import reverse_lazy
from core.views import PaginationRedirectMixin, SuperUserRequiredMixin

from events.forms.manager import PromotionForm
from events.models import Promotion

class PromotionListView(SuperUserRequiredMixin, PaginationRedirectMixin, ListView):
    model = Promotion
    context_object_name = 'promotions'
    paginate_by = 25
    template_name = 'events/manager/promotion/list.html'
    success_url: reverse_lazy('events.views.manager.promotion.list')

class PromotionCreateView(CreateView):
    model = Promotion
    form_class = PromotionForm
    prefix = 'promotion'
    template_name = 'events/manager/promotion/create.html'
    success_url: reverse_lazy('events.views.manager.promotion.list')

class PromotionUpdateView(UpdateView):
    model = Promotion
    form_class = PromotionForm
    prefix = 'promotion'
    template_name = 'events/manager/promotion/update.html'
    success_url: reverse_lazy('events.views.manager.promotion.list')

class PromotionDeleteView(DeleteView):
    model = Promotion
    template_name = 'events/manager/promotion/delete.html'
    prefix = 'promotion'
    success_url: reverse_lazy('events.views.manager.promotion.list')
