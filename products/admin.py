from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'stock_quantity')
    search_fields = ('name', 'sku')
