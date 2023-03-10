# Generated by Django 4.1.5 on 2023-01-28 11:26

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_alter_productinsomeorder_managers'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestaurantCoordinates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('restaurant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='restaurant_coordinates', to='foodcartapp.restaurant')),
            ],
        ),
    ]
