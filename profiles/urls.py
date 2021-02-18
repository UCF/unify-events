from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from profiles.views import ProfileUpdate
from profiles.views import ProfileList

from profiles import views

urlpatterns = [
    url(r'^$',
        view=login_required(ProfileList.as_view()),
        name='profiles.views.profile-list'
    ),
    url(r'^settings',
        view=login_required(ProfileUpdate.as_view()),
        name='profiles.views.profile-settings',
    ),
    url(r'^user/(?P<user_id>\d+)/demote', view=views.update_permissions, name='profiles.views.profile-demote', kwargs={'permissions':False}),
    url(r'^user/(?P<user_id>\d+)/promote', view=views.update_permissions, name='profiles.views.profile-promote', kwargs={'permissions':True}),
]
