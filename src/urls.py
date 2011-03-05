from django.views.generic.simple import direct_to_template
from django.conf.urls.defaults   import *
from django.contrib              import admin
import settings

admin.autodiscover()

urlpatterns = patterns('',
	(r'^admin/', include(admin.site.urls)),
	(r'^$', direct_to_template, {'template':'base.html'}),
	url(r'^calendar/', include('events.urls')),
)

handler500 = lambda r: direct_to_template(r, template='500.html')
handler404 = lambda r: direct_to_template(r, template='404.html')

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:],
			'django.views.static.serve',
			{
				'document_root': settings.MEDIA_ROOT,
				'show_indexes' : True,
			}
		),
	)