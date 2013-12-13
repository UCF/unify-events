from datetime import datetime
import logging

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from profiles.forms import UserForm, ProfileForm

log = logging.getLogger(__name__)

@login_required
def settings(request):
    ctx = {'forms': {'user': None, 'profile': None}, 'first_login': request.user.first_login}
    if request.user.first_login:
        tmpl = 'events/manager/firstlogin/profile.html'
    else:
        tmpl = 'events/manager/profiles/profile.html'

    if request.method == 'POST':
        ctx['forms']['user'] = UserForm(request.POST,
                                        instance=request.user,
                                        prefix='user')
        ctx['forms']['profile'] = ProfileForm(request.POST,
                                              instance=request.user.profile,
                                              prefix='profile')
        if ctx['forms']['user'].is_valid() and ctx['forms']['profile'].is_valid():
            try:
                ctx['forms']['user'].save()
                ctx['forms']['profile'].save()

                # Update the last login time otherwise
                # the user will continue to get redirected
                # here.
                if ctx['first_login']:
                    request.user.last_login = datetime.now()
                    request.user.save()
            except Exception, e:
                log.error('Saving failed: %s ' + str(e))
                messages.error(request, 'Saving user profile failed.')
            else:
                messages.success(request, 'Saving user profile succeeded.')
                if ctx['first_login'] or request.user.owned_calendars.count() == 0:
                    return HttpResponseRedirect(reverse('calendar-create'))
                else:
                    return HttpResponseRedirect(reverse('dashboard'))
    else:
        ctx['forms']['user'] = UserForm(instance=request.user, prefix='user')
        ctx['forms']['profile'] = ProfileForm(instance=request.user.profile, prefix='profile')

    return direct_to_template(request, tmpl, ctx)