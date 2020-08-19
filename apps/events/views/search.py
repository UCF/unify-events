import logging

from core.views import MultipleFormatTemplateViewMixin
from django.views.generic.list import ListView
from events.models import Event, Calendar

log = logging.getLogger(__name__)


class GlobalSearchView(MultipleFormatTemplateViewMixin, ListView):
    paginate_by = 25
    template_name = 'search/search.'
    available_formats = ['html', 'json']

    """
    Only return unique events (do not return events copied to other calendars.)
    """
    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = Event.objects.filter(title__icontains=query).filter(created_from=None)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GlobalSearchView, self).get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        context['calendars'] = Calendar.objects.filter(title__icontains=context['query'])
        return context
