# Generated by Django 4.1.5 on 2023-01-03 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_productsinorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('UNPROCESSED', 'Необработанный'), ('PROCESSED', 'Обработанный')], default='UNPROCESSED', max_length=11, verbose_name='статус'),
        ),
    ]