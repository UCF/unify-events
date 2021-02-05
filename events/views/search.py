import logging
from django.db.models import Q

from core.views import MultipleFormatTemplateViewMixin
from django.views.generic.list import ListView
from events.models import Event, Calendar, State
from datetime import datetime
import settings

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
        query_split = query.split(' ')
        if query:
            now = datetime.now().replace(hour=0, minute=0, second=0)

            queryset = Event.objects.filter(
                        Q(title__icontains=query) | Q(calendar__title__icontains=query) |
                        Q(tags__name__in=query_split)
                        ).filter(state__in=State.get_published_states(),
                        ).filter(Q(event_instances__start__gte=now) | Q(event_instances__start__lt=now, event_instances__end__gte=now)
                        ).filter(created_from=None
                        ).filter(calendar__active=True).distinct()
        else:
            queryset = Event.objects.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GlobalSearchView, self).get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        if context['query']:
            context['calendars'] = Calendar.objects.filter(title__icontains=context['query'], active=True)[:settings.CALENDAR_RESULTS_LIMIT]
        else:
            context['calendars'] = Calendar.objects.none()
        return context
