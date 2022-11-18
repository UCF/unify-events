from django.contrib import admin
from django.template.response import TemplateResponse

from django.urls import path

from .models import InternalLink, KeywordPhrase

# Register your models here.

class KeywordPhraseInline(admin.TabularInline):
    model = KeywordPhrase

@admin.register(InternalLink)
class InternalLinkAdmin(admin.ModelAdmin):
    list_display = ['url', 'keywords', 'imported', 'local', 'replacement_count']
    search_fields = ['phrases__phrase', 'url']
    inlines = [
        KeywordPhraseInline
    ]

    def save_model(self, request, obj, form, change) -> None:
        """
        Custom save_model function for ensuring special
        logic when an InternalLink is saved from within
        the admin section.
        """
        obj.from_admin_site = True
        return super().save_model(request, obj, form, change)


    def get_urls(self):
        """
        Adds the custom URL to the admin site
        """
        urls = super().get_urls()

        additional_urls = [
            path('<path:object_id>/stats/', self.admin_site.admin_view(self.internal_link_stats), name='seo_internallink_stats')
        ]

        urls = additional_urls + urls

        return additional_urls + urls


    def internal_link_stats(self, request, object_id):
        """
        Custom admin view for viewing stats
        for InteralLinkRecords
        """
        object = InternalLink.objects.get(id=object_id)
        context = dict(
            self.admin_site.each_context(request),
            object=object
        )
        return TemplateResponse(request, 'seo/admin/internal-link-stats.html', context)


@admin.register(KeywordPhrase)
class KeywordPhraseAdmin(admin.ModelAdmin):
    list_display = ['phrase', 'replacement_count']
    search_fields = ['phrase']

    def get_urls(self):
        """
        Adds the custom URL to the admin site
        """
        urls = super().get_urls()

        additional_urls = [
            path('<path:object_id>/stats/', self.admin_site.admin_view(self.keyword_phrase_stats), name='seo_keywordphrase_stats')
        ]

        urls = additional_urls + urls

        return additional_urls + urls

    def keyword_phrase_stats(self, request, object_id):
        """
        Custom admin view for viewing stats
        for KeywordPhrases
        """
        object = KeywordPhrase.objects.get(id=object_id)
        context = dict(
            self.admin_site.each_context(request),
            object=object
        )
        return TemplateResponse(request, 'seo/admin/keyword-phrase-stats.html', context)
