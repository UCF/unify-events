from django.contrib import admin

from events.models import Event, Calendar, EventInstance, Location

admin.site.register(Calendar)
admin.site.register(Event)
admin.site.register(EventInstance)
admin.site.register(Location)