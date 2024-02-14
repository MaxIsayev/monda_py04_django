from django.contrib import admin
from . import models
from django.utils.translation import gettext_lazy as _

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'total_pages', 'recent_pages', 'owner']
    list_filter = ['owner']
    list_display_links = ['name']

    def total_pages(self, obj: models.Category):
        return obj.pages.count()
    total_pages.short_description = _('total pages')

    def recent_pages(self, obj: models.Category):
        return "; ".join(obj.pages.order_by('-created_at').values_list('name', flat=True)[:3])
    recent_pages.short_description = _('recent pages')

class PageAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'owner', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'page__name', 'owner__last_name', 'owner__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        (_("general").title(), {
            "fields": (
                ('name'),
                'description',
            ),
        }),
        (_("ownership").title(), {
            "fields": (
                ('owner', 'category'),
            ),
        }),
        (_("temporal tracking").title(), {
            "fields": (
                ('created_at', 'updated_at', 'id'),
            ),
        }),
    )

# Register your models here.
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Page, PageAdmin)
