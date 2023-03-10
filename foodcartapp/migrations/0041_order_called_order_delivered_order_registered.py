# Generated by Django 4.1.5 on 2023-01-03 18:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='called',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Осуществлен звонок'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivered',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Доставлен'),
        ),
        migrations.AddField(
            model_name='order',
            name='registered',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Оформлен'),
            preserve_default=False,
        ),
    ]
