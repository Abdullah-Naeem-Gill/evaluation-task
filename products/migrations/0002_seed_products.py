from decimal import Decimal

from django.db import migrations


def seed_products(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    products = [
        {
            'name': 'Widget Pro',
            'sku': 'WDG-PRO-001',
            'price': Decimal('29.99'),
            'quantity_on_hand': 150,
        },
        {
            'name': 'Gadget Basic',
            'sku': 'GDG-BAS-002',
            'price': Decimal('14.50'),
            'quantity_on_hand': 0,
        },
        {
            'name': 'Cable Pack',
            'sku': 'CBL-PK-003',
            'price': Decimal('9.99'),
            'quantity_on_hand': 42,
        },
    ]
    for product_data in products:
        Product.objects.create(**product_data)


def unseed_products(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Product.objects.filter(
        sku__in=['WDG-PRO-001', 'GDG-BAS-002', 'CBL-PK-003'],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_products, unseed_products),
    ]
