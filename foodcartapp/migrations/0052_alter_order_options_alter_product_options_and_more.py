from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_restaurantcoordinates'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
        migrations.AlterModelOptions(
            name='productcategory',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='restaurant',
            options={'verbose_name': 'Ресторан', 'verbose_name_plural': 'Рестораны'},
        ),
        migrations.AlterModelOptions(
            name='restaurantmenuitem',
            options={'verbose_name': 'Пункт меню ресторана', 'verbose_name_plural': 'Пункты меню ресторана'},
        ),
        migrations.RenameField(
            model_name='order',
            old_name='restaurant',
            new_name='restaurant_cooking_order',
        ),
        migrations.AlterField(
            model_name='productinsomeorder',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='foodcartapp.order', verbose_name='заказ'),
        ),
        migrations.AlterField(
            model_name='productinsomeorder',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='foodcartapp.product', verbose_name='продукт'),
        ),
    ]
