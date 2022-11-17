from django.contrib import admin

from .models import InternalLink, KeywordPhrase

# Register your models here.

class KeywordPhraseInline(admin.TabularInline):
    model = KeywordPhrase

@admin.register(InternalLink)
class InternalLinkAdmin(admin.ModelAdmin):
    list_display = ['url', 'imported', 'local']
    search_fields = ['pattern', 'url']
    inlines = [
        KeywordPhraseInline
    ]

    def save_model(self, request, obj, form, change) -> None:
        obj.from_admin_site = True
        return super().save_model(request, obj, form, change)

