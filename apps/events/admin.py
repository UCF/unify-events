from django.contrib import admin
from events.models import *

admin.site.register(Calendar)
admin.site.register(Event)
admin.site.register(EventInstance)