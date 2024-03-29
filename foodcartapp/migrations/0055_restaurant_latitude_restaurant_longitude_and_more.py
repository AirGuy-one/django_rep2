# Generated by Django 4.1.3 on 2023-03-18 08:24

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_alter_productinsomeorder_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='latitude',
            field=models.DecimalField(decimal_places=6, default=53.564541, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('-90.0')), django.core.validators.MaxValueValidator(Decimal('90.0'))], verbose_name='широта'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant',
            name='longitude',
            field=models.DecimalField(decimal_places=6, default=37.646654, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('-180.0')), django.core.validators.MaxValueValidator(Decimal('180.0'))], verbose_name='долгота'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='RestaurantCoordinates',
        ),
    ]
