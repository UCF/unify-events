import logging

from haystack.views import SearchView

from events.models import Event

log = logging.getLogger(__name__)


class GlobalSearchView(SearchView):
    """
    Only return unique events (do not return events copied to other calendars.)
    Prioritize Main Calendar events.
    """
    def get_results(self):
        results = super(GlobalSearchView, self).get_results()
        results = results.filter(created_from='None') # Yes, this has to be a string. Haystack will not return results by NoneType.

        return results