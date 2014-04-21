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
from django.views.generic import ListView

from util import LDAPHelper
from events.models import Calendar
from events.models import Event
from events.models import EventInstance
from events.models import get_all_users_future_events
from events.models import get_events_by_range
from events.models import State
from events.views.event_views import CalendarEventsBaseListView
from events.views.manager.calendar import CalendarUserValidationMixin


MDAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


class Dashboard(CalendarUserValidationMixin, CalendarEventsBaseListView):
    template_name = 'events/manager/dashboard.html'

    def get_end_date(self):
        """
        Get the end date if for day view.
        """
        end_date = super(Dashboard, self).get_end_date()
        if not end_date and self.is_date_selected():
            end_date = self.get_start_date() + timedelta(days=1) - timedelta(seconds=1)
            self.end_date = end_date

        return end_date

    def get_queryset(self):
        """
        Get queryset based on date and state.
        """
        events = None
        calendar = self.get_calendar()
        if calendar:
            if not self.request.user.is_superuser and calendar not in self.request.user.calendars:
                return HttpResponseNotFound('You do not have permission to access this calendar.')

            if self.is_date_selected():
                events = calendar.range_event_instances(self.get_start_date(), self.get_end_date())
            else:
                events = calendar.future_event_instances()
        else:
            if self.is_date_selected():
                events = get_events_by_range(self.get_start_date(),
                                             self.get_end_date(),
                                             user=self.request.user)
            else:
                events = get_all_users_future_events(self.request.user)

        # get the state filter
        if self.kwargs.get('state') == 'subscribed' and events:
            events = events.filter(event__state=State.get_id('posted'), event__created_from__isnull=False)
        else:
            state_id = State.get_id(self.kwargs.get('state'))
            if state_id is None:
                state_id = State.get_id('posted')

            if events:
                events = events.filter(event__state=state_id)

        self.queryset = events
        return events

    def get_context_data(self, **kwargs):
        """
        Set context for managers Dashboard.
        """
        context = super(Dashboard, self).get_context_data(**kwargs)

        ctx = {
            'rereview_count': None,
            'pending_count': None,
            # Needed to determine whether to show the cancel/un-cancel button
            'posted_state': State.posted,
            'state': 'posted',
            'start_date': self.get_start_date(),
        }

        # merge context data
        ctx.update(context)

        calendar = self.get_calendar()
        if calendar:
            ctx['rereview_count'] = calendar.future_event_instances().filter(event__state=State.rereview).count()
            ctx['pending_count'] = calendar.future_event_instances().filter(event__state=State.pending).count()
        else:
            ctx['rereview_count'] = get_all_users_future_events(self.request.user).filter(event__state=State.rereview).count()
            ctx['pending_count'] = get_all_users_future_events(self.request.user).filter(event__state=State.pending).count()

        # get the state filter
        state_id = State.get_id(self.kwargs.get('state'))
        if state_id is None and self.kwargs.get('state') == 'subscribed':
            ctx['state'] = 'subscribed'
        elif state_id is not None:
            ctx['state'] = self.kwargs.get('state')

        return ctx

    def render_to_response(self, context, **response_kwargs):
        """
        Make sure the user checks their profile when they
        log in for the first time
        """
        if self.request.user.first_login:
            return HttpResponseRedirect(reverse('profile-settings'))
        else:
            return super(Dashboard, self).render_to_response(context, **response_kwargs)
