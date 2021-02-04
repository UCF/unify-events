import logging

from events.views.search import GlobalSearchView
from json_views.views import JSONDataView

from events.models import Event, Calendar
from django.contrib.auth.models import User
from django.db.models import Q

from taggit.models import Tag

log = logging.getLogger(__name__)

class ManagerSearchView(GlobalSearchView):
    template_name = 'search/manager-search.'

    """
    Only return Event results that exist on the current user's
    calendars.
    """
    def get_queryset(self):
        results = super(ManagerSearchView, self).get_queryset()
        results = results.filter(calendar__in=self.request.user.active_calendars)

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
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(username__icontains=q)
            )

            for user in users:
                name_text = ''
                if user.first_name != '':
                    name_text += "{0} ".format(user.first_name)
                if user.last_name != '':
                    name_text += "{0} ".format(user.last_name)
                if user.username != '':
                    name_text += "- {0}".format(user.username) if len(name_text) > 0 else user.username

                r = {
                    'id': user.username,
                    'text': name_text
                }
                results.append(r)

        context['results'] = results

        return context

class CalendarSelect2ListView(JSONDataView):
    def get_context_data(self, **kwargs):
        context = super(CalendarSelect2ListView, self).get_context_data(**kwargs)
        results = []
        q = self.request.GET.get('q', None)

        calendars = None

        if self.request.user.is_superuser:
            calendars = Calendar.objects.filter(active=True)
        else:
            calendars = self.request.user.active_calendars

        if q is not None and len(q) > 2:
            calendars = calendars.filter(title__icontains=q)

        for calendar in calendars:
            r = {
                'id': calendar.id,
                'text': calendar.title
            }

            results.append(r)

        context['results'] = results

        return context

class TagTypeaheadSearchView(JSONDataView):
    def get_context_data(self, **kwargs):
        context = super(TagTypeaheadSearchView, self).get_context_data(**kwargs)
        results = []
        q = self.request.GET.get('q', None)

        tags = Tag.objects.none()

        if q is not None and len(q) > 2:
            tags = Tag.objects.filter(name__icontains=q)

        for tag in tags:
            # 10 points for exact match!
            score = 10 if q.lower() == tag.name else 5

            # High score if the tag is promoted
            score += 200 if tag.is_promoted else 0

            # Add 1 point for each tagged item in the system
            score += tag.taggit_taggeditem_items.count()

            r = {
                'id': tag.id,
                'text': tag.name,
                'score': score
            }

            results.append(r)

        context['results'] = sorted(results, key = lambda i: i['score'], reverse=True)

        return context


