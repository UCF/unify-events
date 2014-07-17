import logging

from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.db.models.loading import get_model
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from core.utils import format_to_mimetype
from events.models import Calendar

log = logging.getLogger(__name__)


def esi_template(request, path):
    """
    Returns ESI code if not in DEV mode.
    """
    return render_to_response(path, {}, RequestContext(request))


def esi(request, model_name, object_id, template_name, calendar_id=None):
    """
    Returns the HTML for a given model and id for ESIs
    """
    app_label = 'events'
    try:
        if model_name == 'tag':
            app_label = 'taggit'

        model = get_model(app_label=app_label, model_name=model_name)
        object_id_int = int(object_id)
        the_object = model.objects.get(pk=object_id_int)
        template_html = template_name.replace('/', '') + '.html'
        url = 'esi/' + model_name + '/' + template_html

        context = { 'object': the_object }

        if calendar_id is not None and calendar_id != 'None':
            calendar_id_int = int(calendar_id)
            calendar = Calendar.objects.get(pk=calendar_id_int)
            context['calendar'] = calendar

        return render_to_response(url, context, RequestContext(request))
    except TypeError:
        log.error('Unable to convert ID to int for model %s from app %s. Object ID: %s ; Calendar ID: %s' % (model_name, app_label, object_id, calendar_id))
    except LookupError:
        log.error('Unable to get model %s from app %s with template %s.' % (model_name, app_label, template))
    except ObjectDoesNotExist:
        log.error('Unable to get the object with pk %s from model %s from app %s with template %s or calendar with pk %s.' % (object_id, model_name, app_label, template, calendar_id))

    raise Http404


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


class DeleteSuccessMessageMixin(object):
    """
    Give the ability to display success messages
    for the DeleteView class.
    """
    success_message = None

    def delete(self, request, *args, **kwargs):
        """
        Set success message if one exists.
        """
        httpResponse = super(DeleteSuccessMessageMixin, self).delete(request, *args, **kwargs)
        success_message = self.get_success_message()
        if success_message:
            messages.success(self.request, success_message)
        return httpResponse

    def get_success_message(self):
        return self.success_message


class MultipleFormatTemplateViewMixin(object):
    """
    Returns a template name based on template_name and
    the url parameter of format.
    """
    template_name = None
    available_formats = ['html', 'json', 'xml', 'rss', 'ics']

    def get_format(self):
        """
        Determine the page format passed in the URL. Fall back to html
        if nothing is set.
        """
        if self.request.GET.get('format') is not None:
            # Backwards compatibility with UNL events
            if self.request.GET.get('format') == 'hcalendar':
                format = 'ics'
            else:
                format = self.request.GET.get('format')
        elif 'format' in self.kwargs and self.kwargs['format'] in self.available_formats:
            format = self.kwargs['format']
        else:
            format = 'html'

        return format

    def get_template_names(self):
        """
        Return the template name based on the format requested.
        """
        format = self.get_format()
        return [self.template_name + format]

    def render_to_response(self, context, **kwargs):
        """
        Set the mimetype of the response based on the format.
        """
        self.kwargs['format'] = self.get_format()
        return super(MultipleFormatTemplateViewMixin, self).render_to_response(context,
                                                                               content_type=format_to_mimetype(self.kwargs['format']),
                                                                               **kwargs)


class PaginationRedirectMixin(object):
    """
    Attempts to redirect to the last valid page in a paginated list if the
    requested page does not exist (instead of returning a 404.)
    """
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page_size = self.get_paginate_by(queryset)
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        url_name = self.request.resolver_match.url_name
        try:
            return super(PaginationRedirectMixin, self).get(request, *args, **kwargs)
        except Http404:
            if self.request.GET.get('page') > paginator.num_pages:
                # Get the current page url and append the new page number:
                url = '%s?page=%s' % (reverse(url_name, kwargs=self.kwargs), paginator.num_pages)
                return HttpResponseRedirect(url)
            else:
                # re-raise Http404, as the reason for the 404 was not that maximum pages was exceeded
                raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})


class ConditionalRedirectMixin(object):
    """
    Sets up methods for defining whether or not a view should redirect
    elsewhere on load.  By default, this mixin won't do anything useful;
    view_should_redirect() and do_redirect() need to be overridden where
    this mixin is used.

    Useful for redirecting urls with an incorrect object slug to the correct
    url when an object's name has changed.
    """
    def view_should_redirect(self):
        """
        Returns true if the view should be redirected.
        """
        return false

    def do_redirect(self):
        """
        Defines where a view should redirect to when self.do_redirect() returns true.
        """
        return super(ConditionalRedirectMixin, self).dispatch(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        Check if a redirect should be done here, and perform whatever redirect
        rules are defined if true.
        """
        if self.view_should_redirect():
            return self.do_redirect()
        else:
            return super(ConditionalRedirectMixin, self).dispatch(request, *args, **kwargs)

