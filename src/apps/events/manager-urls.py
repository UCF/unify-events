from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('',
	url(r'^login/$', view='django.contrib.auth.views.login', kwargs={'template_name':'events/manager/login.html'})
)

urlpatterns += patterns('events.manager-views',
	url(r'^$', view='manager', name='manager'),
	
)
