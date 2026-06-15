from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'sku',
            'price',
            'stock_quantity',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
