from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse_lazy


class SuccessUrlReverseKwargsMixin(object):
    """
    Mixin used to do reverse url lookups
    based on view name using kwargs.
    """
    success_view_name = ''
    copy_kwargs = []

    def get_success_url(self):
        """
        Return url to based on view name
        """
        kwargs = dict()
        for keyword in self.copy_kwargs:
            kwargs[keyword] = self.kwargs[keyword]
        return reverse_lazy(self.success_view_name, kwargs=kwargs)

class FirstLoginTemplateMixin(object):
    """
    Designate an alternate template for a view
    when the user has logged in for the first time
    """
    first_login_template_name = ''

    def get_template_names(self):
        """
        Display the First Login profile update template if necessary
        """
        if len(self.request.user.calendars.all()) == 0 and self.request.user.first_login:
            tmpl = [self.first_login_template_name]
        else:
            tmpl = [self.template_name]

        return tmpl

class SuperUserRequiredMixin(object):
    """
    Require that the user accessing the view is a superuser.
    Return 403 Forbidden if false.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden('You do not have permission to access this page.')
        else:
            return super(SuperUserRequiredMixin, self).dispatch(request, *args, **kwargs)