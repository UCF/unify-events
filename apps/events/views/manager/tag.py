import logging

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from taggit.models import Tag
from events.models import Event
from django.views.generic import TemplateView

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

    ctx['tags'] = Tag.objects.annotate(event_count=Count('taggit_taggeditem_items')).order_by('name')

    # Pagination
    if ctx['tags'] is not None:
        paginator = Paginator(ctx['tags'], 20)
        page = request.GET.get('page', 1)
        try:
            ctx['tags'] = paginator.page(page)
        except PageNotAnInteger:
            ctx['tags'] = paginator.page(1)
        except EmptyPage:
            ctx['tags'] = paginator.page(paginator.num_pages)

    return TemplateView.as_view(request, tmpl, ctx)

@login_required
def create_update(request, tag_id=None):
    ctx = {'form': None, 'mode': 'create', 'tag': None}
    tmpl = 'events/manager/tag/create_update.html'

    if tag_id is not None:
        ctx['mode'] = 'update'
        ctx['tag'] = get_object_or_404(Tag, pk=tag_id)

        if not request.user.is_superuser:
            return HttpResponseForbidden('You cannot modify the specified tag.')
    else:
        if not request.user.is_superuser:
            return HttpResponseForbidden('You cannot create a tag.')

    if request.method == 'POST':
        ctx['form'] = TagForm(request.POST, instance=ctx['tag'])
        if ctx['form'].is_valid():
            tag = ctx['form'].save()
        return HttpResponseRedirect(reverse('tag-list'))
    else:
        ctx['form'] = TagForm(instance=ctx['tag'])

    return TemplateView.as_view(request, tmpl, ctx)

@login_required
def merge(request, tag_from_id=None, tag_to_id=None):
    """
    View for merging the tag into another tag.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot perform this action.')

    if tag_from_id and tag_to_id:
        tag_from = get_object_or_404(Tag, pk=tag_from_id)
        tag_to = get_object_or_404(Tag, pk=tag_to_id)

        events = Event.objects.filter(tags__name__in=[tag_from.name])
        try:
            for event in events:
                event.tags.add(tag_to)
                event.save()
            tag_from.delete()
        except Exception, e:
            log.error(str(e))
            messages.error(request, 'Merging tag failed.')
        else:
            messages.success(request, 'Tag successfully merged.')
        return HttpResponseRedirect(reverse('tag-list'))

    raise Http404

@login_required
def delete(request, tag_id=None):
    tag = get_object_or_404(Tag, pk=tag_id)

    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot delete the specified tag.')

    try:
        tag.delete()
    except Exception, e:
        log(str(e))
        messages.error(request, 'Deleting tag failed.')
    else:
        messages.success(request, 'Tag successfully deleted.')
        return HttpResponseRedirect(reverse('tag-list'))
