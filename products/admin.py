from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku', 'price', 'stock_quantity')
    search_fields = ('name', 'sku')
    readonly_fields = ('id', 'created_at', 'updated_at')
