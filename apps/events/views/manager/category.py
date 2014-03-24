import logging

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from events.forms.manager import CategoryForm
from events.models import Category
from events.models import Event

log = logging.getLogger(__name__)


@login_required
def list(request):
    """
    View for listing out categories.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot view the category manager.')

    ctx = {'categories': None}
    tmpl = 'events/manager/category/list.html'

    ctx['categories'] = Category.objects.all()

    # Pagination
    if ctx['categories'] is not None:
        paginator = Paginator(ctx['categories'], 20)
        page = request.GET.get('page', 1)
        try:
            ctx['categories'] = paginator.page(page)
        except PageNotAnInteger:
            ctx['categories'] = paginator.page(1)
        except EmptyPage:
            ctx['categories'] = paginator.page(paginator.num_pages)

    return TemplateView.as_view(request, tmpl, ctx)

@login_required
def create_update(request, category_id=None):
    """
    View for creating and updating the category.
    """
    ctx = {'category': None, 'form': None, 'mode': 'create'}
    tmpl = 'events/manager/category/create_update.html'

    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot create/modify a category.')

    if category_id:
        ctx['mode'] = 'update'
        ctx['category'] = get_object_or_404(Category, pk=category_id)

    if request.method == 'POST':
        ctx['form'] = CategoryForm(request.POST, instance=ctx['category'])
        if ctx['form'].is_valid():
            try:
                ctx['form'].save()
            except Exception, e:
                log.error(str(e))
                messages.error(request, 'Saving category failed.')
            return HttpResponseRedirect(reverse('category-list'))
    else:
        ctx['form'] = CategoryForm(instance=ctx['category'])
    return direct_to_template(request, tmpl, ctx)

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
        return HttpResponseRedirect(reverse('category-list'))

    raise Http404

@login_required
def delete(request, category_id=None):
    category = get_object_or_404(Category, pk=category_id)

    if not request.user.is_superuser or category.events.count() > 0:
        return HttpResponseForbidden('You cannot delete the specified category.')

    try:
        category.delete()
    except Exception, e:
        log(str(e))
        messages.error(request, 'Deleting category failed.')
    else:
        messages.success(request, 'Category successfully deleted.')
        return HttpResponseRedirect(reverse('category-list'))
