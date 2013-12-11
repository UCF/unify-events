import logging

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from events.forms.manager import CategoryForm
from events.models import Category

log = logging.getLogger(__name__)


@login_required
def list(request):
    """
    View for listing out categories.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot view the category manager.')

    ctx = {'locations': None}
    tmpl = 'events/manager/category/list.html'

    ctx['categories'] = Category.objects.all()

    return direct_to_template(request, tmpl, ctx)

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