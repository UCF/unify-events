import logging

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
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
from events.forms.manager import TagForm
from events.models import Event

log = logging.getLogger(__name__)


class TagListView(SuperUserRequiredMixin, PaginationRedirectMixin, ListView):
    context_object_name = 'tags'
    model = Tag
    paginate_by = 25
    template_name = 'events/manager/tag/list.html'

    def get_queryset(self):
        queryset = super(TagListView, self).get_queryset().order_by('name')
        return queryset.annotate(event_count=Count('taggit_taggeditem_items'))


class TagCreateView(SuperUserRequiredMixin, SuccessPreviousViewRedirectMixin, SuccessMessageMixin, CreateView):
    model = Tag
    template_name = 'events/manager/tag/create_update.html'
    form_class = TagForm
    success_url = reverse_lazy('tag-list')
    success_message = '%(name)s was created successfully.'


class TagUpdateView(SuperUserRequiredMixin, SuccessPreviousViewRedirectMixin, SuccessMessageMixin, UpdateView):
    model = Tag
    template_name = 'events/manager/tag/create_update.html'
    success_url = reverse_lazy('tag-list')
    form_class = TagForm
    success_message = '%(name)s was created successfully.'


class TagDeleteView(SuperUserRequiredMixin, SuccessPreviousViewRedirectMixin, DeleteSuccessMessageMixin, DeleteView):
    model = Tag
    template_name = 'events/manager/tag/delete.html'
    success_url = reverse_lazy('tag-list')
    success_message = 'Tag deleted successfully.'


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
