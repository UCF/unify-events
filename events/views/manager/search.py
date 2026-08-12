import logging

from events.views.search import GlobalSearchView
from django.views.generic import View
from django.http import JsonResponse

from core.views import SuperUserRequiredMixin
from events.functions import format_featured_event_label
from events.functions import get_featurable_events
from events.models import Event, Calendar, Location
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

class UserSelect2ListView(View):
    def get_context_data(self, **kwargs):
        context = {}
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

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return JsonResponse(context)

class CalendarSelect2ListView(View):
    def get_context_data(self, **kwargs):
        context = {}
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

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return JsonResponse(context)

class EventSelect2ListView(SuperUserRequiredMixin, View):
    """
    Feeds the select2 event picker on the featured event form.

    Superuser-gated to match the featured event views themselves -- the list of
    what is publishable on the main calendar isn't secret, but there's no
    reason to serve it to anyone who can't act on it.
    """
    page_size = 25

    def get_context_data(self, **kwargs):
        q = self.request.GET.get('q', None)

        events = get_featurable_events()
        if q:
            events = events.filter(title__icontains=q)

        # Ask for one more than a page so we can tell select2 whether to keep
        # scrolling, without a second COUNT query over the whole match set.
        offset = (self.get_page() - 1) * self.page_size
        page = list(events[offset:offset + self.page_size + 1])
        more = len(page) > self.page_size

        results = [
            {
                'id': event.pk,
                'text': format_featured_event_label(event.title, event.next_start)
            }
            for event in page[:self.page_size]
        ]

        return {
            'results': results,
            'pagination': {'more': more}
        }

    def get_page(self):
        try:
            return max(1, int(self.request.GET.get('page', 1)))
        except (TypeError, ValueError):
            return 1

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return JsonResponse(context)


class TagTypeaheadSearchView(View):
    def get_context_data(self, **kwargs):
        context = {}
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
                'score': score,
                'promoted': tag.is_promoted
            }

            results.append(r)

        context['results'] = sorted(results, key = lambda i: i['score'], reverse=True)

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return JsonResponse(context)

class LocationTypeaheadSearchView(View):
    def get_context_data(self, **kwargs):
        context = {}
        results = []
        q = self.request.GET.get('q', None)

        locations = Location.objects.none();

        if q is not None and len(q) > 2:
            locations = Location.objects.filter(
                Q(title__icontains=q) |
                Q(room__icontains=q)
            )

        for location in locations:
            r = {
                'id': location.pk,
                'title': location.title,
                'comboname': location.comboname,
                'room': location.room,
                'url': location.url
            }

            results.append(r)

        context['results'] = results

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return JsonResponse(context)
