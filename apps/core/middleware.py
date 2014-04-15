import re

class UrlPatters:
    def process_request(self, request):
        if re.match('^/events/', request.path_info):
            setattr(request, 'urlconf', 'events_urls')
