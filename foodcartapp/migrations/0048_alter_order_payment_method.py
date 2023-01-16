# Generated by Django 4.1.3 on 2023-01-16 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_alter_restaurantmenuitem_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('CASH', 'Наличностью'), ('ELECTRONICALLY', 'Электронно')], max_length=14, null=True, verbose_name='способ оплаты'),
        ),
    ]