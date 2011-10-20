from django.contrib.auth.decorators  import login_required
from django.views.generic.simple     import direct_to_template
from datetime                        import datetime, timedelta, date
from events.models                   import Event, Calendar, EventInstance, Tag
from django.contrib                  import messages
from django.http                     import HttpResponseRedirect,HttpResponse,HttpResponseNotFound
from django.core.urlresolvers        import reverse
from events.forms.manager            import EventForm,EventInstanceForm
from django.forms.models             import modelformset_factory
from django.db.models                import Q
from util                            import LDAPHelper
from django.conf                     import settings
from django.utils                    import simplejson
import logging

MDAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

@login_required
def dashboard(request, _date=None, calendar_id = None, search_results = None, tag_name = None):
	ctx  = {
		'instances'  :None,
		'current_calendar':None,
		'dates':{
			'prev_day'      : None,
			'prev_month'    : None,
			'today'         : None,
			'next_day'      : None,
			'next_month'    : None,
			'relative'      : None,
		},
		'tag'           : None,
		'search_results': search_results
	}
	tmpl = 'events/manager/dashboard.html'

	# Make sure check their profile when they
	# log in for the first time
	if request.user.first_login:
		return HttpResponseRedirect(reverse('accounts-profile'))
	
	# Date navigation
	ctx['dates']['today'] = date.today()
	if _date is not None:
		ctx['dates']['relative'] = datetime(*[int(i) for i in _date.split('-')]).date()
	else:
		ctx['dates']['relative'] = ctx['dates']['today']
	
	ctx['dates']['prev_day']   = str((ctx['dates']['relative'] - timedelta(days=1)))
	ctx['dates']['prev_month'] = str((ctx['dates']['relative'] - timedelta(days=MDAYS[ctx['dates']['today'].month])))
	ctx['dates']['next_day']   = str((ctx['dates']['relative'] + timedelta(days=1)))
	ctx['dates']['next_month'] = str((ctx['dates']['relative'] + timedelta(days=MDAYS[ctx['dates']['today'].month])))
	ctx['dates']['today_str']  = str(ctx['dates']['today'])

	if tag_name is not None:
		try:
			ctx['tag'] = Tag.objects.get(name=tag_name)
		except Tag.DoesNotExist:
			return HttpResponseNotFound('Tag specified does not exist.')
		else:
			ctx['instances'] = EventInstance.objects.filter(event__in = ctx['tag'].events.all())
	elif search_results is not None:
		ctx['instances'] = EventInstance.objects.filter(event__in = search_results)
	elif calendar_id is None:
		user_calendars = request.user.calendars
		if len(user_calendars) > 0:
			ctx['current_calendar'] = user_calendars[0]
	else:
		try:
			ctx['current_calendar'] = Calendar.objects.get(pk = calendar_id)
		except Calendar.DoesNotExist:
			messages.error('Calendar does not exist')
	
	if ctx['current_calendar'] is not None:
		ctx['instances'] = ctx['current_calendar'].events_and_subs.filter(start__gte=ctx['dates']['relative'])
	
	return direct_to_template(request,tmpl,ctx)

@login_required
def search_user(request,lastname,firstname=None):
	LDAP_RESULT_LIMIT = 10
	results           = []
	filter_param      = lastname
	filter_string     = '(sn=%s*)'
	
	if firstname is not None:
		filter_param  = (lastname,firstname)
		filter_string = '(&(sn=%s*)(givenName=%s*))'

	if len(lastname) > 3:
		try:
			ldap_helper = LDAPHelper()
			LDAPHelper.bind(ldap_helper.connection,settings.LDAP_NET_SEARCH_USER,settings.LDAP_NET_SEARCH_PASS)
			ldap_results = LDAPHelper.search(ldap_helper.connection,filter_param,filter_string)
			
			for ldap_result in ldap_results:
				try:
					results.append({
						'lastname' :LDAPHelper.extract_lastname(ldap_result),
						'firstname':LDAPHelper.extract_firstname(ldap_result),
						'username' :LDAPHelper.extract_username(ldap_result),
						'guid'     :LDAPHelper.extract_guid(ldap_result),
						})
				except LDAPHelper.MissingAttribute:
					pass
		except Exception, e:
			logging.error(str(e))
	return HttpResponse(simplejson.dumps(results),mimetype='application/json')

@login_required
def search_event(request):
	query   = request.GET.get('query', '')
	results = []
	if query != '':
		results = Event.objects.filter(Q(title__icontains=query)|Q(description__icontains=query))
	
	return dashboard(request, search_results=results)