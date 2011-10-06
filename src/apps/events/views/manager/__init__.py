from django.contrib.auth.decorators  import login_required
from django.views.generic.simple     import direct_to_template

@login_required
def manage(request):
	ctx  = {}
	tmpl = 'events/manager/splash.html'

	if request.user.first_login:
		return HttpResponseRedirect(reverse('accounts-profile'))
	
	return direct_to_template(request,tmpl,ctx)