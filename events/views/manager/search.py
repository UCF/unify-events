import logging

from events.views.search import GlobalSearchView
from json_views.views import JSONDataView

from events.models import Event
from django.contrib.auth.models import User
from django.db.models import Q

log = logging.getLogger(__name__)

class ManagerSearchView(GlobalSearchView):
    template_name = 'search/manager-search.'

    """
    Only return Event results that exist on the current user's
    calendars.
    """
    def get_queryset(self):
        results = super(ManagerSearchView, self).get_queryset()
        results = results.filter(calendar__in=self.request.user.calendars)

        return results

    def get_context_data(self, **kwargs):
        return super(ManagerSearchView, self).get_context_data(**kwargs)

class UserSelect2ListView(JSONDataView):
    def get_context_data(self, **kwargs):
        context = super(UserSelect2ListView, self).get_context_data(**kwargs)
        results = []
        q = self.request.GET.get('q', None)

        if q is not None and len(q) > 2:
            users = User.objects.filter(
                Q(first_name__icontains=q) or
                Q(last_name__icontains=q) or
                Q(username__icontains=q)
            )

            for user in users:
                r = {
                    'id': user.username,
                    'text': "{0} {1} - {2}".format(user.first_name, user.last_name, user.username)
                }
                results.append(r)

        context['results'] = results

        return context

