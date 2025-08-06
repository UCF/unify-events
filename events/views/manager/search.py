import logging

from events.views.search import GlobalSearchView
from django.views.generic import View
from django.http import JsonResponse

from events.models import Event, Calendar, Location, get_main_calendar
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from django.db.models import Count

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


class SuggestedCalendarSelect2ListView(View):
    def get_context_data(self, **kwargs):
        context = {}
        results = []
        q = self.request.GET.get('q', None)
        requesting_calendar_id = self.request.GET.get('calendar', None)

        if not requesting_calendar_id:
            context['results'] = []
            return context

        calendar = None

        try:
            calendar = Calendar.objects.get(pk=requesting_calendar_id)
        except Calendar.DoesNotExist:
            context['results'] = []
            return context

        if not calendar.is_main_calendar:
            valid_tier = calendar.tier - 1
            calendars = Calendar.objects.filter(tier=valid_tier)

            for c in calendars:
                result = {
                    'id': c.id,
                    'text': c.title
                }

                results.append(result)

        context['results'] = results
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return JsonResponse(context)

class FeaturedEventSelect2ListView(View):
    def get_context_data(self, **kwargs):
        context = {}
        results = []
        q = self.request.GET.get('q', None)

        main_calendar = get_main_calendar()

        if not main_calendar:
            context['results'] = []
            return context

        events = Event.objects.filter(
            title__icontains=q,
            calendar=main_calendar,
            event_instances__start__gte=timezone.now().date()
        ).values(
            'id',
            'title'
        ).annotate(
            Count('id')
        )

        for e in events:
            result = {
                'id': e['id'],
                'text': e['title']
            }

            results.append(result)

        context['results'] = results
        return context

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
