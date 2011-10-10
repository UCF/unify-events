from django.contrib.auth.decorators  import login_required
from django.views.generic.simple     import direct_to_template
from datetime                        import datetime, timedelta, date
from ..events.models                 import Event, Calendar, EventInstance
from django.contrib                  import messages
from django.http                     import HttpResponseRedirect
from django.core.urlresolvers        import reverse
from ..events.forms.manager          import EventForm,EventInstanceForm
from django.forms.models             import modelformset_factory
from django.db.models                import Q

MDAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

@login_required
def manage(request, _date=None, calendar_id = None):
	ctx  = {
		'events'  :None,
		'calendar':None,
		'dates':{
			'prev_day'  : None,
			'prev_month': None,
			'today'     : None,
			'next_day'  : None,
			'next_month': None,
			'realative' : None,
		},
		'event_form'   : None,
		'event_formset': None,
	}
	tmpl = 'events/manager/manage.html'

	# Make sure check their profile when they
	# log in for the first time
	if request.user.first_login:
		return HttpResponseRedirect(reverse('accounts-profile'))
	
	# Date navigation
	ctx['dates']['today'] = date.today()
	if _date is not None:
		ctx['dates']['relative'] = datetime(*[int(i) for i in _date.split('-')])
	else:
		ctx['dates']['relative'] = ctx['dates']['today']

	ctx['dates']['prev_day']   = str(ctx['dates']['relative'] - timedelta(days=1))
	ctx['dates']['prev_month'] = str(ctx['dates']['relative'] - timedelta(days=MDAYS[ctx['dates']['today'].month]))
	ctx['dates']['next_day']   = str(ctx['dates']['relative'] + timedelta(days=1))
	ctx['dates']['next_month'] = str(ctx['dates']['relative'] + timedelta(days=MDAYS[ctx['dates']['today'].month]))

	if calendar_id is None: # Upcoming events
		ctx['events'] = request.user.owned_events.filter(instances__start__gte = ctx['dates']['today'])
	else:
		try:
			ctx['calendar'] = Calendar.objects.get(pk = calendar_id)
		except Calendar.DoesNotExist:
			messages.error('Calendar does not exist')
		else:
			ctx['events'] = ctx['calendar'].events.all()

	return direct_to_template(request,tmpl,ctx)