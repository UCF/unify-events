import logging

from haystack.generic_views import SearchView

from core.views import MultipleFormatTemplateViewMixin
from events.models import Event

log = logging.getLogger(__name__)


class GlobalSearchView(MultipleFormatTemplateViewMixin, SearchView):
    template_name = 'search/search.'
    available_formats = ['html', 'json']

    """
    Only return unique events (do not return events copied to other calendars.)
    """
    def get_queryset(self):
        queryset = super(GlobalSearchView, self).get_queryset()
        queryset = queryset.filter(created_from='None') # Yes, this has to be a string. Haystack will not return results by NoneType
        return queryset
