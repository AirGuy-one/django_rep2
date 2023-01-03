# Generated by Django 4.1.5 on 2023-01-03 20:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='foodcartapp.restaurant', verbose_name='ресторан'),
        ),
        migrations.AlterField(
            model_name='order',
            name='called',
            field=models.DateTimeField(blank=True, null=True, verbose_name='осуществлен звонок'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivered',
            field=models.DateTimeField(blank=True, null=True, verbose_name='доставлен'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('CASH', 'Наличностью'), ('ELECTRONICALLY', 'Электронно')], default='ELECTRONICALLY', max_length=14, verbose_name='способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='registered',
            field=models.DateTimeField(auto_now_add=True, verbose_name='оформлен'),
        ),
    ]