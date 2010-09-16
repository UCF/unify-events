from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('',
	url(r'^(?P<calendar>[\w]+)/$', include('events.urls')),
)

from django.views.generic.simple import direct_to_template
handler500 = lambda r: direct_to_template(r, template='500.html')
handler404 = lambda r: direct_to_template(r, template='404.html')

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
			'django.views.static.serve',
			{
				'document_root': settings.MEDIA_ROOT,
				'show_indexes' : True,
			}
		),
	)