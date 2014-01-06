from datetime import datetime
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from profiles.models import Profile

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

@login_required
def list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden('You do not have permission to access this page.')

    ctx = {
        'users': User.objects.all(),
    }
    tmpl = 'events/manager/profiles/list.html'

    # Pagination
    if ctx['users'] is not None:
        paginator = Paginator(ctx['users'], 20)
        page = request.GET.get('page', 1)
        try:
            ctx['users'] = paginator.page(page)
        except PageNotAnInteger:
            ctx['users'] = paginator.page(1)
        except EmptyPage:
            ctx['users'] = paginator.page(paginator.num_pages)

    return direct_to_template(request, tmpl, ctx)

@login_required
def update_permissions(request, user_id=None, permissions=False):
    if not isinstance(permissions, bool):
        return HttpResponseNotFound('Invalid modification to the user was specified.')

    try:
        modified_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponseNotFound('The user you are trying to modify does not exist.')
    else:
        if not request.user.is_superuser:
            return HttpResponseForbidden('You cannot modify the specified user.')
        try:
            modified_user.is_staff = permissions
            modified_user.is_superuser = permissions
            modified_user.save()
        except Exception, e:
            log.error(str(e))
            messages.error(request, 'Updating user permissions failed.')
        else:
            messages.success(request, 'User permissions successfully updated.')

    return HttpResponseRedirect(reverse('profile-list'))