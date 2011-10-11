from django.contrib.auth.decorators  import login_required
from django.views.generic.simple     import direct_to_template
from django.http                     import HttpResponseNotFound, HttpResponseForbidden,HttpResponseRedirect
from django.core.urlresolvers        import reverse
from django.contrib                  import messages
from events.models                   import Calendar
from events.forms.manager            import CalendarForm

@login_required
def create_update(request, id = None):
	ctx = {'form':None,'mode':'create','calendar':None}
	tmpl = 'events/manager/calendar/create_update.html'

	if id is not None:
		ctx['mode'] = 'update'
		try:
			ctx['calendar'] = Calendar.objects.get(pk = id)
		except Calendar.DoesNotExist:
			return HttpResponseNotFound('The calendar specified does not exist')
	
	if request.method == 'POST':
		ctx['form'] = CalendarForm(request.POST,instance=ctx['calendar'])
		if ctx['form'].is_valid():
			calendar = ctx['form'].save(commit=False)
			calendar.creator = request.user
			calendar.save()
	else:
		ctx['form'] = CalendarForm(instance=ctx['calendar'])
	
	return direct_to_template(request,tmpl,ctx)