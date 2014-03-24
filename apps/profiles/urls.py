from django.conf.urls import patterns
from django.conf.urls import url

urlpatterns = patterns(
    'profiles.views',
    url(r'^$', view='list', name='profile-list'),
    url(r'^settings/$', view='settings', name='profile-settings'),
    url(r'^user/(?P<user_id>\d+)/demote', view='update_permissions', name='profile-demote', kwargs={'permissions':False}),
    url(r'^user/(?P<user_id>\d+)/promote', view='update_permissions', name='profile-promote', kwargs={'permissions':True}),
)
