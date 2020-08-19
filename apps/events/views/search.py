import logging
from django.db.models import Q

from core.views import MultipleFormatTemplateViewMixin
from django.views.generic.list import ListView
from events.models import Event, Calendar, State
from datetime import datetime

log = logging.getLogger(__name__)


class GlobalSearchView(MultipleFormatTemplateViewMixin, ListView):
    paginate_by = 25
    template_name = 'search/search.'
    available_formats = ['html', 'json']

    """
    Only return unique events (do not return events copied to other calendars.)
    """
    def get_queryset(self):
        query = self.request.GET.get('q', None)
        if query:
            queryset = Event.objects.filter(Q(title__icontains=query) | Q(calendar__title__icontains=query)) \
                        .filter(state__in=State.get_published_states(), event_instances__start__gte=datetime.now()) \
                        .filter(created_from=None)
        else:
            queryset = Event.objects.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GlobalSearchView, self).get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        if context['query']:
            context['calendars'] = Calendar.objects.filter(title__icontains=context['query'])
        else:
            context['calendars'] = Calendar.objects.none()
        return context
