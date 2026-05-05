from django.contrib import admin
from django.utils.html import format_html
from .models import Price, PriceHistory


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'market', 'formatted_price_display', 'date', 'quality', 'is_verified', 'recorded_by')
    list_filter = ('market', 'product__category', 'date', 'is_verified', 'quality')
    search_fields = ('product__name', 'market__name')
    autocomplete_fields = ('product', 'market')
    date_hierarchy = 'date'
    list_per_page = 50

    fieldsets = (
        ('Asosiy', {
            'fields': ('product', 'market', 'price', 'date')
        }),
        ('Tafsilotlar', {
            'fields': ('quality', 'is_verified', 'notes')
        }),
        ('Texnik', {
            'fields': ('recorded_at', 'recorded_by'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('recorded_at',)

    def formatted_price_display(self, obj):
        return format_html(
            '<strong style="color: #16a34a;">{} so\'m</strong>',
            f"{obj.price:,.0f}".replace(',', ' ')
        )
    formatted_price_display.short_description = 'Narxi'

    def save_model(self, request, obj, form, change):
        if not obj.recorded_by:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'market', 'old_price', 'new_price', 'change_percent_display', 'changed_at')
    list_filter = ('market', 'product__category')
    search_fields = ('product__name',)
    readonly_fields = ('product', 'market', 'old_price', 'new_price', 'change_percent', 'changed_at')

    def change_percent_display(self, obj):
        color = '#dc2626' if obj.change_percent > 0 else '#16a34a'
        symbol = '↑' if obj.change_percent > 0 else '↓'
        return format_html(
            '<span style="color: {};">{} {}%</span>',
            color, symbol, abs(obj.change_percent)
        )
    change_percent_display.short_description = "O'zgarish"

    def has_add_permission(self, request):
        return False
