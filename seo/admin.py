from django.contrib import admin

from .models import AutoAnchor

# Register your models here.
@admin.register(AutoAnchor)
class AutoAnchorAdmin(admin.ModelAdmin):
    list_display = ['pattern', 'url', 'imported', 'local']
    search_fields = ['pattern', 'url']

    def save_model(self, request, obj, form, change) -> None:
        print("Custom save_model called")
        obj.from_admin_site = True
        return super().save_model(request, obj, form, change)
