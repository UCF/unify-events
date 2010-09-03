from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('',
	#(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	#(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
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