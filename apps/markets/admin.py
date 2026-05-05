from django.contrib import admin
from django.utils.html import format_html
from .models import Market


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'working_hours', 'phone', 'is_active', 'order', 'color_preview')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Asosiy', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Manzil va joylashuv', {
            'fields': ('address', 'latitude', 'longitude')
        }),
        ('Ish vaqti va aloqa', {
            'fields': ('working_hours', 'phone')
        }),
        ('Sozlamalar', {
            'fields': ('color', 'is_active', 'order')
        }),
    )

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 30px; height: 20px; background: {}; border-radius: 4px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Rang'
