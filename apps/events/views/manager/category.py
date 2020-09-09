import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from core.views import SuperUserRequiredMixin
from core.views import DeleteSuccessMessageMixin
from core.views import PaginationRedirectMixin
from core.views import SuccessPreviousViewRedirectMixin
from core.views import success_previous_view_redirect
from events.forms.manager import CategoryForm
from events.models import Category

log = logging.getLogger(__name__)


class CategoryCreate(SuperUserRequiredMixin, SuccessPreviousViewRedirectMixin, SuccessMessageMixin, CreateView):
    form_class = CategoryForm
    model = Category
    success_message = '%(title)s was created successfully.'
    success_url = reverse_lazy('events.views.manager.category-list')
    template_name = 'events/manager/category/create_update.html'


class CategoryUpdate(SuperUserRequiredMixin, SuccessPreviousViewRedirectMixin, SuccessMessageMixin, UpdateView):
    form_class = CategoryForm
    model = Category
    success_message = '%(title)s was updated successfully.'
    success_url = reverse_lazy('events.views.manager.category-list')
    template_name = 'events/manager/category/create_update.html'


class CategoryDelete(SuperUserRequiredMixin, SuccessPreviousViewRedirectMixin, DeleteSuccessMessageMixin, DeleteView):
    form_class = CategoryForm
    model = Category
    success_message = 'Category was deleted successfully.'
    success_url = reverse_lazy('events.views.manager.category-list')
    template_name = 'events/manager/category/delete.html'

    def post(self, request, *args, **kwargs):
        category = self.get_object()
        if category.events.count() > 0:
            return HttpResponseForbidden('This category has events assigned to it and cannot be deleted.')
        return self.delete(request, *args, **kwargs)


class CategoryList(SuperUserRequiredMixin, PaginationRedirectMixin, ListView):
    context_object_name = 'categories'
    model = Category
    paginate_by = 25
    template_name = 'events/manager/category/list.html'

    def get_context_data(self, **kwargs):
        """
        Add location list to context.
        """
        context = super(CategoryList, self).get_context_data(**kwargs)

        context['category_list'] = Category.objects.all()

        return context


@login_required
def merge(request, category_from_id=None, category_to_id=None):
    """
    View for merging the category into another category.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot perform this action.')

    if category_from_id and category_to_id:
        category_from = get_object_or_404(Category, pk=category_from_id)
        category_to = get_object_or_404(Category, pk=category_to_id)

        events = category_from.events.all()
        if events.count() > 0:
            try:
                for event in events:
                    event.category = category_to
                    event.save()
                category_from.delete()
            except Exception, e:
                log.error(str(e))
                messages.error(request, 'Merging category failed.')
            else:
                messages.success(request, 'Category successfully merged.')
        else:
            messages.error(request, 'Cannot merge this category: category has no events. Delete this category instead of merging.')
        return success_previous_view_redirect(request, reverse('events.views.manager.category-list'))

    raise Http404
