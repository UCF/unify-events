from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView

from events.models import State
from events.views.manager import Dashboard
from events.views.manager.calendar import CalendarCreate
from events.views.manager.calendar import CalendarDelete
from events.views.manager.calendar import CalendarUpdate
from events.views.manager.calendar import CalendarUserUpdate
from events.views.manager.calendar import CalendarSubscriptionsUpdate
from events.views.manager.calendar import SubscribeToCalendar
from events.views.manager.calendar import CalendarList
from events.views.manager.category import CategoryCreate
from events.views.manager.category import CategoryUpdate
from events.views.manager.category import CategoryDelete
from events.views.manager.category import CategoryList
from events.views.manager.event import EventCreate
from events.views.manager.event import EventDelete
from events.views.manager.event import EventUpdate
from events.views.manager.location import LocationCreateView
from events.views.manager.location import LocationDeleteView
from events.views.manager.location import LocationListView
from events.views.manager.location import LocationUpdateView
from events.views.manager.tag import TagCreateView
from events.views.manager.tag import TagDeleteView
from events.views.manager.tag import TagListView
from events.views.manager.tag import TagUpdateView
from events.views.manager.promotion import PromotionListView
from events.views.manager.promotion import PromotionCreateView
from events.views.manager.promotion import PromotionUpdateView
from events.views.manager.promotion import PromotionDeleteView

from events.views.manager import event
from events.views.manager import calendar
from events.views.manager import category
from events.views.manager import location
from events.views.manager import tag

from events.views.manager.search import CalendarSelect2ListView, ManagerSearchView
from events.views.manager.search import UserSelect2ListView
from events.views.manager.search import SuggestedCalendarSelect2ListView
from events.views.manager.search import TagTypeaheadSearchView
from events.views.manager.search import LocationTypeaheadSearchView

urlpatterns = [
    url(r'^login/$',
        view=LoginView.as_view(template_name='events/manager/login.html'),
        name='accounts-login'),
    url(r'^logout/$',
        view=LogoutView.as_view(template_name='events/manager/logout.html'),
        name='accounts-logout')
]

urlpatterns += [

    url(r'^event/(?P<pk>\d+)/copy', view=event.copy, name='events.views.manager.event-copy'),
    url(r'^event/(?P<pk>\d+)/update', login_required(EventUpdate.as_view()), name='events.views.manager.event-update'),
    url(r'^event/(?P<pk>\d+)/submit-to-main', view=event.submit_to_main, name='events.views.manager.event-submit-to-main'),
    url(r'^event/(?P<pk>\d+)/post', view=event.update_state, name='events.views.manager.event-post', kwargs={'state':State.posted}),
    url(r'^event/(?P<pk>\d+)/pend', view=event.update_state, name='events.views.manager.event-pend', kwargs={'state':State.pending}),
    url(r'^event/(?P<pk>\d+)/cancel', view=event.cancel_uncancel, name='events.views.manager.event-cancel-uncancel'),
    url(r'^event/(?P<pk>\d+)/delete', login_required(EventDelete.as_view()), name='events.views.manager.event-delete'),
    url(r'^event/(?P<pk>\d+)/state', login_required(event.get_event_state), name='events.views.manager.get-event-state'),
    url(r'^event/create', login_required(EventCreate.as_view()), name='events.views.manager.event-create'),
    url(r'^event/bulk-action/', view=event.bulk_action, name='events.views.manager.event-bulk-action'),

    url(r'^calendar/create/?$',
        view=login_required(CalendarCreate.as_view()),
        name='events.views.manager.calendar-create'
    ),
    url(r'^calendar/(?P<pk>\d+)/delete/?$',
        view=login_required(CalendarDelete.as_view()),
        name='events.views.manager.calendar-delete'
    ),
    url(r'^calendar/(?P<pk>\d+)/update/?$',
        view=login_required(CalendarUpdate.as_view()),
        name='events.views.manager.calendar-update'
    ),
    url(r'^calendar/(?P<pk>\d+)/update/users/?$',
        view=login_required(CalendarUserUpdate.as_view()),
        name='events.views.manager.calendar-update-users'
    ),
    url(r'^calendar/(?P<pk>\d+)/update/subscriptions/?$',
        view=login_required(CalendarSubscriptionsUpdate.as_view()),
        name='events.views.manager.calendar-update-subscriptions'
    ),
    url(r'^calendar/(?P<pk>\d+)/(?P<state>[\w]+)?$', login_required(Dashboard.as_view()), name='events.views.manager.dashboard-calendar-state'),
    url(r'^calendar/(?P<pk>\d+)/update/user/(?P<username>[\w]+)/(?P<role>[\w]+)?$', view=calendar.add_update_user, name='events.views.manager.calendar-add-update-user'),
    url(r'^calendar/(?P<pk>\d+)/delete/user/(?P<username>[\w]+)', view=calendar.delete_user, name='events.views.manager.calendar-delete-user'),
    url(r'^calendar/(?P<pk>\d+)/reassign-ownership/user/(?P<username>[\w]+)', view=calendar.reassign_ownership, name='events.views.manager.calendar-reassign-ownership'),
    url(r'^calendar/(?P<pk>\d+)/unsubscribe-from/(?P<subscribed_calendar_id>\d+)?$', view=calendar.unsubscribe_from_calendar, name='events.views.manager.calendar-unsubscribe'),
    url(r'^calendar/subscribe-to/(?P<pk>\d+)?$',
        view=login_required(SubscribeToCalendar.as_view()),
        name='events.views.manager.calendar-subscribe'
    ),
    url(r'^calendar/(?P<pk>\d+)/?$', login_required(Dashboard.as_view()), name='dashboard'),
    url(r'^calendar/(?P<pk>\d+)/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/?$',
        login_required(Dashboard.as_view()),
        name='events.views.manager.manager-day-listing'
    ),
    url(r'^(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/?$',
        login_required(Dashboard.as_view()),
        name='events.views.manager.manager-all-calendars-day-listing'
    ),
    url(r'^all-calendars/?$',
        view=login_required(CalendarList.as_view()),
        name='events.views.manager.calendar-list'
    ),

    url(r'^location/?$', login_required(LocationListView.as_view()), name='events.views.manager.location-list'),
    url(r'^location/search/?$', login_required(LocationTypeaheadSearchView.as_view()), name='events.views.manager.location-search'),
    url(r'^location/create/?$', login_required(LocationCreateView.as_view()), name='events.views.manager.location-create'),
    url(r'^location/(?P<pk>\d+)/update', login_required(LocationUpdateView.as_view()), name='events.views.manager.location-update'),
    url(r'^location/(?P<location_from_id>\d+)/merge/(?P<location_to_id>\d+)', view=location.merge, name='events.views.manager.location-merge'),
    url(r'^location/(?P<pk>\d+)/delete', login_required(LocationDeleteView.as_view()), name='events.views.manager.location-delete'),
    url(r'^location/(?P<state>[\w]+)?$', login_required(LocationListView.as_view()), name='events.views.manager.location-state'),
    url(r'^location/bulk-action/', view=location.bulk_action, name='events.views.manager.location-bulk-action'),

    url(r'^tag/?$', login_required(TagListView.as_view()), name='events.views.manager.tag-list'),
    url(r'^tag/create/?$', login_required(TagCreateView.as_view()), name='events.views.manager.tag-create'),
    url(r'^tag/(?P<pk>\d+)/update/?$', login_required(TagUpdateView.as_view()), name='events.views.manager.tag-update'),
    url(r'^tag/(?P<tag_from_id>\d+)/merge/(?P<tag_to_id>\d+)', view=tag.merge, name='events.views.manager.tag-merge'),
    url(r'^tag/(?P<tag_id>\d+)/promote/?$', view=tag.promote_tag, name='events.views.manager.tag-promote'),
    url(r'^tag/(?P<tag_id>\d+)/demote/?$', view=tag.demote_tag, name='events.views.manager.tag-demote'),
    url(r'^tag/(?P<pk>\d+)/delete', login_required(TagDeleteView.as_view()), name='events.views.manager.tag-delete'),
    url(r'^tag/search', login_required(TagTypeaheadSearchView.as_view()), name='events.views.manager.tag-search'),

    url(r'promotion/?$', login_required(PromotionListView.as_view()), name='events.views.manager.promotion.list'),
    url(r'promotion/create/?$', login_required(PromotionCreateView.as_view()), name='events.views.manager.promotion.create'),
    url(r'promotion/(?P<pk>\d+)/update/?$', login_required(PromotionUpdateView.as_view()), name='events.views.manager.promotion.update'),
    url(r'promotion/(?P<pk>\d+)/delete/?$', login_required(PromotionDeleteView.as_view()), name='events.views.manager.promotion.delete'),

    url(r'^category/create/?$',
        view=login_required(CategoryCreate.as_view()),
        name='events.views.manager.category-create'
    ),
    url(r'^category/(?P<pk>\d+)/update/?$',
        view=login_required(CategoryUpdate.as_view()),
        name='events.views.manager.category-update'
    ),
    url(r'^category/(?P<pk>\d+)/delete/?$',
        view=login_required(CategoryDelete.as_view()),
        name='events.views.manager.category-delete'
    ),
    url(r'^category/?$',
        view=login_required(CategoryList.as_view()),
        name='events.views.manager.category-list'
    ),
    url(r'^category/(?P<category_from_id>\d+)/merge/(?P<category_to_id>\d+)',
        view=category.merge,
        name='events.views.manager.category-merge'
    ),
    url(r'^userselect2/?$', login_required(UserSelect2ListView.as_view()), name='events.views.manager.user-select2'),
    url(r'^calendarselect2/?$', login_required(CalendarSelect2ListView.as_view()), name='events.views.manager.calendar-select2'),
    url(r'^suggestedselect2/?$', login_required(SuggestedCalendarSelect2ListView.as_view()), name='events.views.manager.suggested-select2'),
    url(r'^profiles/', include('profiles.urls')),

    url(r'^$', login_required(Dashboard.as_view()), name='dashboard'),
    url(r'^state/(?P<state>[\w]+)?$', login_required(Dashboard.as_view()), name='dashboard-state'),
]

# Search-related URLs
urlpatterns += [
    url(r'^search/$', login_required(ManagerSearchView.as_view()), name='search_manager_view'),
]
