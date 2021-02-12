from django.http.response import HttpResponseRedirect
from events.models.event import PromotedTag
import logging

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from taggit.models import Tag

from core.views import DeleteSuccessMessageMixin
from core.views import SuperUserRequiredMixin
from core.views import PaginationRedirectMixin
from core.views import SuccessPreviousViewRedirectMixin
from core.views import success_previous_view_redirect
from events.forms.manager import TagForm
from events.models import Event

log = logging.getLogger(__name__)

class TagListView(SuperUserRequiredMixin, PaginationRedirectMixin, ListView):
    context_object_name = 'tags'
    model = Tag
    paginate_by = 25
    template_name = 'events/manager/tag/list.html'

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        promoted = self.request.GET.get('promoted', False)

        queryset = super(TagListView, self).get_queryset().order_by('name')

        if q:
            queryset = queryset.filter(name__icontains=q)

        if promoted:
            queryset = queryset.filter(promoted__isnull=False)

        return queryset.annotate(event_count=Count('taggit_taggeditem_items'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        promoted = PromotedTag.objects.all()
        context['promoted_tags'] = promoted

        return context

class TagCreateView(SuperUserRequiredMixin, SuccessPreviousViewRedirectMixin, SuccessMessageMixin, CreateView):
    model = Tag
    template_name = 'events/manager/tag/create_update.html'
    form_class = TagForm
    success_url = reverse_lazy('events.views.manager.tag-list')
    success_message = '%(name)s was created successfully.'


class TagUpdateView(SuperUserRequiredMixin, SuccessPreviousViewRedirectMixin, SuccessMessageMixin, UpdateView):
    model = Tag
    template_name = 'events/manager/tag/create_update.html'
    success_url = reverse_lazy('events.views.manager.tag-list')
    form_class = TagForm
    success_message = '%(name)s was created successfully.'


class TagDeleteView(SuperUserRequiredMixin, SuccessPreviousViewRedirectMixin, DeleteSuccessMessageMixin, DeleteView):
    model = Tag
    template_name = 'events/manager/tag/delete.html'
    success_url = reverse_lazy('events.views.manager.tag-list')
    success_message = 'Tag deleted successfully.'

@login_required
def promote_tag(request, tag_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot perform this action.')

    try:
        original_tag = Tag.objects.get(pk=tag_id)
    except Tag.DoesNotExist:
        messages.error(request, f'Tag with ID {tag_id} does not exist.')
        return success_previous_view_redirect(request, reverse('events.views.manager.tag-list'))

    try:
        existing = PromotedTag.objects.get(tag=original_tag)
        messages.success(request, f'Tag {existing.tag.name} is already promoted.')
    except PromotedTag.DoesNotExist:
        tag = PromotedTag.objects.create(tag=original_tag)
        messages.success(request, f'Tag {tag.tag.name} is now promoted.')

    return success_previous_view_redirect(request, reverse('events.views.manager.tag-list'))

@login_required
def demote_tag(request, tag_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot perform this action.')

    try:
        existing = PromotedTag.objects.get(tag__id=tag_id)
        existing.delete()
        messages.success(request, f'Tag {existing.tag.name} has been demoted.')
    except PromotedTag.DoesNotExist:
        try:
            tag = Tag.objects.get(pk=tag_id)
            messages.error(request, f'Tag {tag.name} cannot be demoted.')
        except Tag.DoesNotExist:
            messages.error(request, f'Tag with the ID {tag_id} does not exist.')

    return success_previous_view_redirect(request, reverse('events.views.manager.tag-list'))


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
        except Exception as e:
            log.error(str(e))
            messages.error(request, 'Merging tag failed.')
        else:
            messages.success(request, 'Tag successfully merged.')
        return success_previous_view_redirect(request, reverse('events.views.manager.tag-list'))

    raise Http404
