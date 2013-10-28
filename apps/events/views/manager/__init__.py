from datetime import datetime, timedelta, date
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.utils import simplejson
from django.views.generic.simple import direct_to_template

from util import LDAPHelper
from events.models import Event, Calendar, get_all_users_future_events
from events.functions import format_to_mimetype


MDAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


@login_required
def dashboard(request, _date=None, calendar_id=None, search_results=None, format=None, day=None, month=None, year=None):
    ctx = {
        'instances': None,
        'current_calendar': None,
        'events': None,
        'dates': {
            'prev_day': None,
            'prev_month': None,
            'today': None,
            'next_day': None,
            'next_month': None,
            'relative': None,
        },
        'search_results': search_results,
        'owned_calendars': len(request.user.owned_calendars.all())
    }
    tmpl = 'events/manager/dashboard.html'

    # Make sure check their profile when they
    # log in for the first time
    if request.user.first_login:
        return HttpResponseRedirect(reverse('profile-settings'))

    if calendar_id:
        current_calendar = get_object_or_404(Calendar, pk=calendar_id)
        if current_calendar not in request.user.calendars:
            return HttpResponseNotFound('You do not have permission to access this calendar.')
        ctx['current_calendar'] = current_calendar
        ctx['events'] = current_calendar.future_event_instances
    else:
        ctx['events'] = get_all_users_future_events(request.user)

    # Date navigation
    ctx['dates']['today'] = date.today()
    if _date is not None:
        ctx['dates']['relative'] = datetime(*[int(i) for i in _date.split('-')]).date()
    else:
        ctx['dates']['relative'] = ctx['dates']['today']

    ctx['dates']['prev_day'] = str((ctx['dates']['relative'] - timedelta(days=1)))
    ctx['dates']['prev_month'] = str((ctx['dates']['relative'] - timedelta(days=MDAYS[ctx['dates']['today'].month])))
    ctx['dates']['next_day'] = str((ctx['dates']['relative'] + timedelta(days=1)))
    ctx['dates']['next_month'] = str((ctx['dates']['relative'] + timedelta(days=MDAYS[ctx['dates']['today'].month])))
    ctx['dates']['today_str'] = str(ctx['dates']['today'])

    # Pagination
    if ctx['instances'] is not None:
        paginator = Paginator(ctx['instances'], 10)
        page = request.GET.get('page', 1)
        try:
            ctx['instances'] = paginator.page(page)
        except PageNotAnInteger:
            ctx['instances'] = paginator.page(1)
        except EmptyPage:
            ctx['instances'] = paginator.page(paginator.num_pages)

    return direct_to_template(request, tmpl, ctx, mimetype=format_to_mimetype(format))


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