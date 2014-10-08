import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.views.generic import UpdateView

from core.views import FirstLoginTemplateMixin
from core.views import SuperUserRequiredMixin
from core.views import PaginationRedirectMixin
from profiles.forms import UserForm

log = logging.getLogger(__name__)


class ProfileUpdate(FirstLoginTemplateMixin, SuccessMessageMixin, UpdateView):
    form_class = UserForm
    model = User
    success_message = 'Profile was updated successfully.'
    success_url = reverse_lazy('profile-settings')
    template_name = 'events/manager/profiles/profile.html'
    first_login_template_name = 'events/manager/firstlogin/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            if request.user.first_login:
                return HttpResponseRedirect(reverse_lazy('calendar-create'))
            else:
                return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ProfileList(SuperUserRequiredMixin, PaginationRedirectMixin, ListView):
    context_object_name = 'users'
    model = User
    paginate_by = 25
    template_name = 'events/manager/profiles/list.html'

    def get_queryset(self):
        queryset = super(ProfileList, self).get_queryset()
        return queryset.order_by('-is_superuser', 'last_name', 'first_name')



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
        if not permissions and User.objects.filter(is_superuser=True).count() < 2:
            return HttpResponseForbidden('You cannot demote this user; no more superusers would be left!')

        try:
            modified_user.is_staff = permissions
            modified_user.is_superuser = permissions
            modified_user.save()
        except Exception, e:
            log.error(str(e))
            messages.error(request, 'Updating user permissions failed.')
        else:
            messages.success(request, 'User permissions successfully updated.')

    # The request user is not updated with changes that have been made to the modified user.
    # This requires a check to see if the usernames match and whether they have superuser permissions.
    if request.user.username != modified_user.username or (request.user.username == modified_user.username and modified_user.is_superuser):
        return HttpResponseRedirect(reverse('profile-list'))
    else:
        return HttpResponseRedirect(reverse('dashboard'))
