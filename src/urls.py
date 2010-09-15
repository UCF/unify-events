from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('',
	url(r'^(?P<calendar>[\w]+)/$', include('events.urls')),
)

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