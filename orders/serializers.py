from decimal import Decimal

from rest_framework import serializers

from products.models import Product

from .models import Order, OrderItem
from .services import OrderServiceError, create_order


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'items', 'total']

    def get_total(self, obj):
        return sum(
            (item.quantity * item.unit_price for item in obj.items.all()),
            Decimal('0'),
        )


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than zero.')
        return value


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Order must contain at least one item.')
        return value

    def create(self, validated_data):
        request = self.context['request']
        try:
            return create_order(request.user, validated_data['items'])
        except OrderServiceError as exc:
            raise serializers.ValidationError({exc.field: exc.message}) from exc
