from django.contrib import admin

from events.models import Calendar
from events.models import Event
from events.models import EventInstance
from events.models import Location
from events.models import Category
from events.models import Promotion

admin.site.register(Event)
admin.site.register(EventInstance)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Promotion)

@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('active', 'tier',)
    list_display = ('title', 'active', 'trusted', 'tier',)
