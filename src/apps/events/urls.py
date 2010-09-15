from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('events.views',
	url(r'^(?P<type>)/events/$', 'event_listing', name='event_listing_html'),
	url(r'^(?P<type>)/events/(?P<format>[\w]+)$', 'event_listing', name='event_listing'),
)