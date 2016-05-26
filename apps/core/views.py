import logging

from collections import namedtuple
import urllib
from urlparse import urljoin
from urlparse import urlparse
from urlparse import parse_qs

from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.http import HttpResponsePermanentRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.db.models.loading import get_model
from django.shortcuts import get_object_or_404
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


def esi(request, model_name, object_id, template_name, calendar_id=None, params=None):
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

        # Add params, if any, to context.
        if params:
            params = parse_qs(params)
            context.update(params)

        if calendar_id is not None and calendar_id != 'None':
            calendar_id_int = int(calendar_id)
            calendar = Calendar.objects.get(pk=calendar_id_int)
            context['calendar'] = calendar

        return render_to_response(url, context, RequestContext(request))
    except TypeError:
        log.error('Unable to convert ID to int for model %s from app %s. Object ID: %s ; Calendar ID: %s' % (model_name, app_label, object_id, calendar_id))
    except LookupError:
        log.error('Unable to get model %s from app %s with template %s.' % (model_name, app_label, template_name))
    except ObjectDoesNotExist:
        log.error('Unable to get the object with pk %s from model %s from app %s with template %s or calendar with pk %s.' % (object_id, model_name, app_label, template_name, calendar_id))

    raise Http404


def handler404(request):
    response = render_to_response('404.html',
                                  {},
                                  RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html',
                                  {},
                                  RequestContext(request))
    response.status_code = 500
    return response


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
        if self.request.GET.get('format'):
            # Backwards compatibility with UNL events
            if self.request.GET.get('format') == 'hcalendar' or self.request.GET.get('format') == 'ical':
                format = 'ics'
            else:
                format = self.request.GET.get('format')
        elif 'format' in self.kwargs and self.kwargs['format'] in self.available_formats:
            format = self.kwargs['format']
        else:
            format = 'html'

        # Fall back to html if an invalid format is passed
        if not format or not format in self.available_formats:
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
    def dispatch(self, request, *args, **kwargs):
        r_kwargs = request.resolver_match.kwargs
        queryset = self.get_queryset()
        page_size = self.get_paginate_by(queryset)
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        url_name = self.request.resolver_match.url_name

        # prevent feed.None from being passed into new redirect url
        if 'format' in r_kwargs and r_kwargs['format'] is None:
            r_kwargs.pop('format', None)

        try:
            return super(PaginationRedirectMixin, self).dispatch(request, *args, **kwargs)
        except Http404:
            if self.request.GET.get('page') > paginator.num_pages:
                # Get the current page url and append the new page number:
                url = '%s?page=%s' % (reverse(url_name, kwargs=r_kwargs), paginator.num_pages)
                return HttpResponseRedirect(url)
            else:
                # re-raise Http404, as the reason for the 404 was not that maximum pages was exceeded
                raise Http404


class InvalidSlugRedirectMixin(object):
    """
    Overrides the dispatch method to perform a 301 redirect when the slug of
    an object in the url is incorrect.

    Useful for redirecting urls with an incorrect object slug to the correct
    url when an object's name has changed.

    Note that this mixin assumes its view utilizes a consistent url
    schema, where the by_model is referenced in the url by '/<by_model>_pk/<by_model>/'
    and an additional calendar filter is referenced by '/<pk>/<slug>/'.
    """
    by_model = None # The primary model by which url context should be derived

    def dispatch(self, request, *args, **kwargs):
        """
        Return a 301 redirect if the provided object slug(s) don't
        match the by_object's actual slug, or dispatch if all is well.
        """

        by_model_lc = str(self.by_model.__name__).lower()
        needs_redirect = False

        # Catch <by_model slug> in url (i.e. Events by Category, Tag)
        if by_model_lc in kwargs:
            by_object_pk = kwargs[by_model_lc + '_pk']
            by_object_slug = kwargs[by_model_lc]
            by_object = get_object_or_404(self.by_model, pk=by_object_pk)

            # If the provided by_object slug is incorrect, fix it
            if by_object_slug != by_object.slug:
                needs_redirect = True
                kwargs[by_model_lc] = by_object.slug

            # Check if a calendar pk/slug are provided (i.e. Events on Calendar by Category, Tag)
            if 'pk' in kwargs:
                calendar_pk = kwargs['pk']
                calendar_slug = kwargs['slug']
                calendar = get_object_or_404(Calendar, pk=calendar_pk)

                # If the provided calendar slug isn't correct, fix it
                if calendar_slug != calendar.slug:
                    needs_redirect = True
                    kwargs['slug'] = calendar.slug
        else:
            by_object_pk = kwargs['pk']
            by_object_slug = kwargs['slug']
            by_object = get_object_or_404(self.by_model, pk=by_object_pk)

            # If the provided by_object slug is incorrect, fix it
            if by_object_slug != by_object.slug:
                needs_redirect = True
                kwargs['slug'] = by_object.slug

        if needs_redirect:
            url_name = request.resolver_match.url_name
            # prevent feed.None from being passed into new redirect url
            if 'format' in kwargs and kwargs['format'] is None:
                kwargs.pop('format', None)

            return HttpResponsePermanentRedirect(reverse(url_name, kwargs=kwargs))
        else:
            return super(InvalidSlugRedirectMixin, self).dispatch(request, *args, **kwargs)


class SuccessPreviousViewRedirectMixin(object):
    """
    Updates the success_url of an EditView to redirect the user to the view
    they were on previously before editing the object.

    Includes validation of specified previous views to prevent arbitrary
    redirection to invalid paths or pages outside of the app.

    NOTE: this mixin depends on the HTTP_REFERER header, which may not be
    100% accurate.  The mixin will also fail when the requested view is opened
    in a new tab or window or requested the view directly by its absolute URL.
    The view's success_url is used as a fallback.
    """
    def path_is_valid(self, path):
        """
        Validates a relative URL path as a legit view.  Returns True if the
        path resolves and False on failure.
        """
        try:
            view, args, kwargs = resolve(path)
            kwargs['request'] = self.request
            if 'delete' not in self.request.path:
                view(*args, **kwargs)
        except Http404:
            # url in 'path' variable did not resolve to a view
            return False
        else:
            return True

    def get_relative_path_with_query(self, absolute_url):
        """
        Parses an absolute url.  Returns a namedtuple containing the following:

        relative: string containing path + query params combination
        path: string containing relative path only
        query: string containing query params only
        """
        retval = namedtuple('RelativePath', ['relative', 'path', 'query'])
        url_parsed = urlparse(absolute_url)
        retval.path = retval.relative = url_parsed.path
        retval.query = url_parsed.query
        if retval.query:
            retval.relative = '%s?%s' % (retval.path, retval.query)
        return retval

    def get_context_data(self, **kwargs):
        """
        Adds 'form_action_next' context for use in Create, Update and Delete
        Views to add query parameters to the <form> element's 'action'
        attribute.
        """
        context = super(SuccessPreviousViewRedirectMixin, self).get_context_data(**kwargs)
        context['form_action_next'] = ''

        next = self.request.META.get('HTTP_REFERER', None)
        if next:
            next_relative = self.get_relative_path_with_query(next)
            success_url = self.success_url
            if next_relative.relative != success_url and self.path_is_valid(next_relative.path):
                context['form_action_next'] = urllib.quote_plus(next)

        return context

    def get_success_url(self):
        """
        Returns the relative path of the url provided in the 'next' param,
        or the view's default success_url if 'next' is invalid or unavailable.
        """
        success_url = super(SuccessPreviousViewRedirectMixin, self).get_success_url()
        next = self.request.GET.get('next')

        if next:
            next = urllib.unquote_plus(next)  # unencode
            next_relative = self.get_relative_path_with_query(next)
            if self.path_is_valid(next_relative.path):
                success_url = next_relative.relative

        return success_url


def success_previous_view_redirect(request, fallback_view_url):
    """
    A simplified, function-based implementation of
    SuccessPreviousViewRedirectMixin.

    Should be used in views that are not class-based when that view should
    redirect back to the previous page on success, instead of a direct
    HttpResponseRedirect call.
    """
    next = fallback_view_url
    try:
        previous_view_url = request.META.get('HTTP_REFERER', None)
        if previous_view_url:
            Mixin = SuccessPreviousViewRedirectMixin()
            prev_relative = Mixin.get_relative_path_with_query(previous_view_url)
            if Mixin.path_is_valid(prev_relative.path):
                next = prev_relative.relative
    except Exception:
        # Just move on/use fallback_view_url
        pass

    return HttpResponseRedirect(next)
