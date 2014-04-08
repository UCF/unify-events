import logging

from haystack.views import SearchView

from events.models import Event

log = logging.getLogger(__name__)


class ManagerSearchView(SearchView):
    """
    Only return Event results that exist on the current user's
    editable calendars.
    """
    def get_results(self):
        results = super(ManagerSearchView, self).get_results()
        results = results.models(Event).filter(calendar__in=self.request.user.editable_calendars)
        return results

    def extra_context(self):
        extra = super(ManagerSearchView, self).extra_context()
        extra['manager_search'] = True
        return extra