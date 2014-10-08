from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from profiles.views import ProfileUpdate
from profiles.views import ProfileList


urlpatterns = patterns(
    'profiles.views',
    url(r'^$',
        view=login_required(ProfileList.as_view()),
        name='profile-list'
    ),
    url(r'^settings',
        view=login_required(ProfileUpdate.as_view()),
        name='profile-settings',
    ),
    url(r'^user/(?P<user_id>\d+)/demote', view='update_permissions', name='profile-demote', kwargs={'permissions':False}),
    url(r'^user/(?P<user_id>\d+)/promote', view='update_permissions', name='profile-promote', kwargs={'permissions':True}),
)