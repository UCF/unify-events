import logging

from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from taggit.models import Tag

from events.forms.manager import TagForm

log = logging.getLogger(__name__)


@login_required
def list(request):
    """
    View for listing out tags.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot view the tag manager.')

    ctx = {'tags': None}
    tmpl = 'events/manager/tag/list.html'

    ctx['tags'] = Tag.objects.all()

    return direct_to_template(request, tmpl, ctx)


@login_required
def update(request, tag_id=None):
    ctx = {'form': None, 'mode': 'update', 'tag': None}
    tmpl = 'events/manager/tag/create_update.html'

    if tag_id is not None:
        ctx['tag'] = get_object_or_404(Tag, pk=tag_id)

        if not request.user.is_superuser:
            return HttpResponseForbidden('You cannot modify the specified tag.')
    else:
        return HttpResponseForbidden('You must select a tag to edit.')

    if request.method == 'POST':
        ctx['form'] = TagForm(request.POST, instance=ctx['tag'])
        if ctx['form'].is_valid():
            tag = ctx['form'].save()
        return HttpResponseRedirect(reverse('tag-list'))
    else:
        ctx['form'] = TagForm(instance=ctx['tag'])

    return direct_to_template(request, tmpl, ctx)
