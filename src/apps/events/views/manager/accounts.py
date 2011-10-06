from django.views.generic.simple    import direct_to_template
from ..events.forms.manager         import UserForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib                 import messages
@login_required
def profile(request, first_login = False):
	ctx  = {'forms':{'user':None,'profile':None},'first_login':first_login}
	tmpl = 'events/manager/accounts/profile.html'

	if request.method == 'POST':
		ctx['forms']['user']    = UserForm(
									request.POST,
									instance=request.user,
									prefix='user')
		ctx['forms']['profile'] = ProfileForm(
									request.POST,
									instance=request.user.profile,
									prefix='profile')
		if ctx['forms']['user'].is_valid() and ctx['forms']['profile'].is_valid():
			ctx['forms']['user'].save()
			ctx['forms']['profile'].save()
	else:
		ctx['forms']['user']    = UserForm(instance=request.user, prefix='user')
		ctx['forms']['profile'] = ProfileForm(instance=request.user.profile,prefix='profile')

	return direct_to_template(request,tmpl,ctx)