from datetime import datetime, timedelta, date
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.views.generic import TemplateView

from util import LDAPHelper
from events.models import Calendar
from events.models import Event
from events.models import get_all_users_future_events
from events.models import get_range_users_events
from events.models import State
from events.functions import format_to_mimetype


MDAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


class Dashboard(TemplateView) :

    template_name = 'events/manager/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)

        # request, calendar_id=None, state=None, search_results=None, year=None, month=None, day=None, format=None
        ctx = {
            'instances': None,
            'current_calendar': None,
            'rereview_count': None,
            'pending_count': None,
            # Needed to determine whether to show the cancel/un-cancel button
            'posted_state': State.posted,
            'state': 'posted',
            'events': None,
            'dates': {
                'prev_day': None, # relative to 'relative' date value
                'prev_month': None, # relative to 'relative' date value
                'today': None, # always today's date
                'today_str': None, # 'today' but in string format
                'next_day': None, # relative to 'relative' date value
                'next_month': None, # relative to 'relative' date value
                'relative': None, # date selected in calendar to view
            },
            'day_view': False,
            'owned_calendars': len(self.request.user.owned_calendars.all())
        }

        # merge context data
        ctx.update(context)

        # Date navigation
        ctx['dates']['today'] = date.today()
        if all(x in ctx for x in ('year', 'month', 'day')):
            try:
                ctx['dates']['relative'] = date(int(year), int(month), int(day))
                ctx['day_view'] = True
            except ValueError: # bad day/month/year vals provided
                ctx['dates']['relative'] = ctx['dates']['today']
        else:
            ctx['dates']['relative'] = ctx['dates']['today']

        ctx['dates']['prev_day'] = str((ctx['dates']['relative'] - timedelta(days=1)))
        ctx['dates']['prev_month'] = str((ctx['dates']['relative'] - timedelta(days=MDAYS[ctx['dates']['today'].month])))
        ctx['dates']['next_day'] = str((ctx['dates']['relative'] + timedelta(days=1)))
        ctx['dates']['next_month'] = str((ctx['dates']['relative'] + timedelta(days=MDAYS[ctx['dates']['today'].month])))
        ctx['dates']['today_str'] = str(ctx['dates']['today'])

        # Get events from calendar(s)
        events = None
        if self.kwargs.get('calendar_id'):
            current_calendar = get_object_or_404(Calendar, pk=self.kwargs.get('calendar_id'))
            if not self.request.user.is_superuser and current_calendar not in self.request.user.calendars:
                return HttpResponseNotFound('You do not have permission to access this calendar.')
            ctx['current_calendar'] = current_calendar
            ctx['rereview_count'] = current_calendar.future_event_instances().filter(event__state=State.rereview).count()
            ctx['pending_count'] = current_calendar.future_event_instances().filter(event__state=State.pending).count()
            if ctx['day_view']:
                start = ctx['dates']['relative']
                end = start + timedelta(days=1) - timedelta(seconds=1)
                events = current_calendar.range_event_instances(start, end)
            else:
                events = current_calendar.future_event_instances()
        else:
            ctx['rereview_count'] = get_all_users_future_events(self.request.user).filter(event__state=State.rereview).count()
            ctx['pending_count'] = get_all_users_future_events(self.request.user).filter(event__state=State.pending).count()
            if ctx['day_view']:
                events = get_range_users_events(self.request.user, ctx['dates']['relative'], ctx['dates']['relative'])
            else:
                events = get_all_users_future_events(self.request.user)

        # get the state filter
        state_id = State.get_id(self.kwargs.get('state'))
        if state_id is not None:
            ctx['state'] = self.kwargs.get('state')
        else:
            state_id = State.get_id('posted')
        events = events.filter(event__state=state_id)
        ctx['events'] = events

        # Pagination
        if ctx['events'] is not None:
            paginator = Paginator(ctx['events'], 10)
            page = self.request.GET.get('page', 1)
            try:
                ctx['events'] = paginator.page(page)
            except PageNotAnInteger:
                ctx['events'] = paginator.page(1)
            except EmptyPage:
                ctx['events'] = paginator.page(paginator.num_pages)

        return ctx


@login_required
def search_user(request, firstname, lastname=None):
    results = []

    if lastname:
        user_qs = User.objects.filter(first_name__startswith=firstname, last_name__startswith=lastname)
    else:
        # Search first or last if only firstname is given
        user_qs = User.objects.filter(Q(first_name__startswith=firstname) | Q(last_name__startswith=firstname))

    # Limit the size of the results and only return the needed User attributes
    if len(user_qs):
        results = list(user_qs.values_list('first_name', 'last_name', 'username')[:settings.USER_SEARCHLIMIT])

    return HttpResponse(simplejson.dumps(results), mimetype='application/json')


@login_required
def search_event(request):
    query = request.GET.get('query', '')
    results = []
    if query != '':
        results = Event.objects.filter(Q(title__icontains=query)|Q(description__icontains=query))
    return dashboard(request, search_results=results)
