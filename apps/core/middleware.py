import re

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class UrlPatterns:
    def process_request(self, request):
        if re.match('^/events/', request.path_info):
            setattr(request, 'urlconf', 'events_urls')


class CorsRegex:
    def process_response(self, request, response):
        if re.match(settings.CORS_REGEX, request.path):
            response['Access-Control-Allow-Origin'] = '*'


class SecureRequiredMiddleware(object):
    def __init__(self):
        self.paths = getattr(settings, 'SECURE_REQUIRED_PATHS')
        self.enabled = self.paths and getattr(settings, 'HTTPS_SUPPORT')

    def process_request(self, request):
        if self.enabled and not request.is_secure():
            for path in self.paths:
                if request.get_full_path().startswith(path):
                    request_url = request.build_absolute_uri(request.get_full_path())
                    secure_url = request_url.replace('http://', 'https://')
                    return HttpResponsePermanentRedirect(secure_url)
        return None

 
"""
Remove instances of multiple spaces in html markup.
This middleware is necessary for IE10 in particular (and possibly
other browsers) to prevent excessive whitespace from preventing the
rendering of a text node.
"""
RE_MULTISPACE = re.compile(r"\s{2,}")
 
class MinifyHTMLMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type'] and settings.COMPRESS_HTML:
            response.content = RE_MULTISPACE.sub(" ", response.content)
        return response