from django.db import transaction

from products.models import Product

from .models import Order, OrderItem


class OrderServiceError(Exception):
    def __init__(self, message, field='items'):
        self.message = message
        self.field = field
        super().__init__(message)


def _aggregate_order_items(items_data):
    """Combine duplicate product lines into a single quantity per product."""
    aggregated = {}
    for item in items_data:
        product = item['product']
        quantity = item['quantity']
        if product.pk in aggregated:
            aggregated[product.pk]['quantity'] += quantity
        else:
            aggregated[product.pk] = {'product': product, 'quantity': quantity}
    return list(aggregated.values())


def create_order(customer, items_data):
    """
    Create an order and its items atomically.

    items_data: iterable of dicts with ``product`` (Product) and ``quantity`` (int).
    Input shape is validated by OrderCreateSerializer before this is called.
    Rolls back entirely if any line fails stock validation.
    """
    aggregated_items = _aggregate_order_items(list(items_data))

    with transaction.atomic():
        product_ids = [item['product'].pk for item in aggregated_items]
        products = {
            product.pk: product
            for product in Product.objects.select_for_update().filter(pk__in=product_ids)
        }

        for item in aggregated_items:
            product = products[item['product'].pk]
            quantity = item['quantity']
            if product.stock_quantity < quantity:
                raise OrderServiceError(
                    (
                        f'Insufficient stock for product "{product.name}" '
                        f'(requested {quantity}, available {product.stock_quantity}).'
                    ),
                    field='items',
                )

        order = Order.objects.create(customer=customer)

        for item in aggregated_items:
            product = products[item['product'].pk]
            quantity = item['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
            )
            product.stock_quantity -= quantity
            product.save(update_fields=['stock_quantity', 'updated_at'])

    return order


def cancel_order(order):
    """Cancel a pending order and restock its items."""
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.status != Order.Status.PENDING:
            raise OrderServiceError(
                'Only pending orders can be cancelled.',
                field='detail',
            )

        for item in order.items.select_related('product'):
            product = Product.objects.select_for_update().get(pk=item.product_id)
            product.stock_quantity += item.quantity
            product.save(update_fields=['stock_quantity', 'updated_at'])

        order.status = Order.Status.CANCELLED
        order.save(update_fields=['status', 'updated_at'])

    return order
