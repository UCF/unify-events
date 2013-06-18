from django.contrib import admin
from events.models import Event, Calendar

admin.site.register(Calendar)
admin.site.register(Event)