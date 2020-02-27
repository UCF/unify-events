import logging

from haystack.generic_views import SearchView

from events.models import Event

log = logging.getLogger(__name__)


class ManagerSearchView(SearchView):
    """
    Only return Event results that exist on the current user's
    calendars.
    """
    def get_queryset(self):
        results = super(ManagerSearchView, self).get_queryset()
        results = results.filter(calendar__in=self.request.user.calendars)

        return results
