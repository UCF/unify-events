from django.contrib import admin

from events.models import Calendar
from events.models import Event
from events.models import EventInstance
from events.models import Location
from events.models import Category
from events.models import Promotion
from events.models import FeaturedEvent
from events.models import get_main_calendar

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


@admin.register(FeaturedEvent)
class FeaturedEventAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(FeaturedEventAdmin, self).get_form(request, obj, **kwargs)
        main_calendar = get_main_calendar()
        if main_calendar:
            form.base_fields['event'].queryset = Event.objects.filter(calendar=main_calendar)

        return form
