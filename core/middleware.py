import re

from django.conf import settings
from django.http import HttpResponsePermanentRedirect, Http404


class UrlPatterns:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if re.match('^/events/', request.path_info):
            setattr(request, 'urlconf', 'events_urls')

        return self.get_response(request)


class CorsRegex:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if re.match(settings.CORS_REGEX, request.path):
            response['Access-Control-Allow-Origin'] = '*'
        else:
            for k in settings.CORS_GET_PARAMS:
                if k in request.GET and re.match(settings.CORS_GET_PARAMS[k], request.GET[k]):
                    response['Access-Control-Allow-Origin'] = '*'
                    break
        return response


class SecureRequiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.paths = getattr(settings, 'SECURE_REQUIRED_PATHS')
        self.enabled = self.paths and getattr(settings, 'HTTPS_SUPPORT')

    def __call__(self, request):
        if self.enabled and not request.is_secure():
            for path in self.paths:
                if request.get_full_path().startswith(path):
                    request_url = request.build_absolute_uri(request.get_full_path())
                    secure_url = request_url.replace('http://', 'https://')
                    return HttpResponsePermanentRedirect(secure_url)
        return self.get_response(request)


"""
Remove instances of multiple spaces in html markup.
This middleware is necessary for IE10 in particular (and possibly
other browsers) to prevent excessive whitespace from preventing the
rendering of a text node.
"""
RE_MULTISPACE = re.compile(r"\s{2,}")

class MinifyHTMLMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if 'text/html' in response['Content-Type'] and settings.COMPRESS_HTML:
            response.content = RE_MULTISPACE.sub(" ", response.content.decode('utf-8'))
        return response
