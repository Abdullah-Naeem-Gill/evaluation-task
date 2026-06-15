import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ('name', models.CharField(max_length=255)),
                ('sku', models.CharField(max_length=100, unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity_on_hand', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
