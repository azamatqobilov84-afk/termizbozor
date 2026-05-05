from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'slug', 'order', 'product_count')
    list_editable = ('order',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Mahsulotlar soni'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'category', 'unit', 'is_active', 'is_popular', 'is_seasonal')
    list_filter = ('category', 'is_active', 'is_popular', 'is_seasonal', 'unit')
    list_editable = ('is_popular', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('category',)

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'slug', 'category', 'unit')
        }),
        ('Rasm', {
            'fields': ('image', 'icon')
        }),
        ('Tafsilotlar', {
            'fields': ('description', 'is_seasonal')
        }),
        ('Sozlamalar', {
            'fields': ('is_active', 'is_popular')
        }),
    )
