from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_seed_products'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='quantity_on_hand',
            new_name='stock_quantity',
        ),
    ]
