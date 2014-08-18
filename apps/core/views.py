import logging

from urlparse import parse_qs

from django.http import Http404
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.http import HttpResponsePermanentRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.db.models.loading import get_model
from django.http import Http404
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
        
        # Add params, if any, to context. Try to catch instance_start and
        # instance_end and convert them back to datetimes.
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
        log.error('Unable to get model %s from app %s with template %s.' % (model_name, app_label, template))
    except ObjectDoesNotExist:
        log.error('Unable to get the object with pk %s from model %s from app %s with template %s or calendar with pk %s.' % (object_id, model_name, app_label, template, calendar_id))

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

        # prevent feed.None from being passed into new redirect url
        if 'format' in self.kwargs and self.kwargs['format'] is None:
            self.kwargs.pop('format', None)

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
        r_kwargs = request.resolver_match.kwargs

        # Catch <by_model slug> in url (i.e. Events by Category, Tag)
        if by_model_lc in r_kwargs:
            by_object_pk = r_kwargs[by_model_lc + '_pk']
            by_object_slug = r_kwargs[by_model_lc]
            by_object = get_object_or_404(self.by_model, pk=by_object_pk)

            # If the provided by_object slug is incorrect, fix it
            if by_object_slug != by_object.slug:
                needs_redirect = True
                r_kwargs[by_model_lc] = by_object.slug

            # Check if a calendar pk/slug are provided (i.e. Events on Calendar by Category, Tag)
            if 'pk' in r_kwargs:
                calendar_pk = r_kwargs['pk']
                calendar_slug = r_kwargs['slug']
                calendar = get_object_or_404(Calendar, pk=calendar_pk)

                # If the provided calendar slug isn't correct, fix it
                if calendar_slug != calendar.slug:
                    needs_redirect = True
                    r_kwargs['slug'] = calendar.slug
        else:
            by_object_pk = r_kwargs['pk']
            by_object_slug = r_kwargs['slug']
            by_object = get_object_or_404(self.by_model, pk=by_object_pk)

            # If the provided by_object slug is incorrect, fix it
            if by_object_slug != by_object.slug:
                needs_redirect = True
                r_kwargs['slug'] = by_object.slug

        if needs_redirect:
            url_name = request.resolver_match.url_name
            # prevent feed.None from being passed into new redirect url
            if 'format' in r_kwargs and r_kwargs['format'] is None:
                r_kwargs.pop('format', None)
                
            return HttpResponsePermanentRedirect(reverse(url_name, kwargs=r_kwargs))
        else:
            return super(InvalidSlugRedirectMixin, self).dispatch(request, *args, **kwargs)

