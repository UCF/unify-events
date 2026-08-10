from django.contrib import admin

from events.forms.manager import FeaturedEventForm
from events.models import Calendar
from events.models import Event
from events.models import EventInstance
from events.models import FeaturedEvent
from events.models import Location
from events.models import Category
from events.models import Promotion

admin.site.register(Calendar)
admin.site.register(Event)
admin.site.register(EventInstance)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Promotion)


@admin.register(FeaturedEvent)
class FeaturedEventAdmin(admin.ModelAdmin):
    # Reuse the manager form so the admin gets the same main-calendar-only
    # event list and the same image size guidance.
    form = FeaturedEventForm
    list_display = ('event', 'start_date')
    list_filter = ('start_date',)
    search_fields = ('event__title',)
