from django.contrib.auth.decorators  import login_required
from django.views.generic.simple     import direct_to_template
from datetime                        import datetime
from ..events.models                 import Event, Calendar
from django.contrib                  import messages

@login_required
def manage(request, calendar_id = None):
	ctx  = {'events':None,'calendar':None}
	tmpl = 'events/manager/manage.html'

	if request.user.first_login:
		return HttpResponseRedirect(reverse('accounts-profile'))

	if calendar_id is None: # Upcoming events
		ctx['events'] = Event.objects.filter(instances__start__gte = datetime.now())
	else:
		try:
			ctx['calendar'] = Calendar.objects.get(pk = calendar_id)
		except Calendar.DoesNotExist:
			messages.error('Calendar does not exist')
		else:
			ctx['events'] = ctx['calendar'].events.all()
			
	return direct_to_template(request,tmpl,ctx)