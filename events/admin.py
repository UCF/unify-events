from django.contrib import admin

from events.models import Calendar
from events.models import Event
from events.models import EventInstance
from events.models import Location
from events.models import Category

admin.site.register(Calendar)
admin.site.register(Event)
admin.site.register(EventInstance)
admin.site.register(Location)
admin.site.register(Category)