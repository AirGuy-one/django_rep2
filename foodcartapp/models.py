import os

from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from dotenv import load_dotenv

from foodcartapp.validators import validate_quantity
from restaurateur.fetch_coordinates import fetch_coordinates


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'Ресторан'
        verbose_name_plural = 'Рестораны'

    def __str__(self):
        return self.name


class RestaurantCoordinates(models.Model):
    restaurant = models.OneToOneField(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='restaurant_coordinates',
    )
    latitude = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    longitude = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        validators=[MinValueValidator(Decimal('0.01'))],
    )


@receiver(post_save, sender=Restaurant)
def update_stock(sender, instance, **kwargs):
    load_dotenv()
    restaurant_coords = fetch_coordinates(
        os.environ['GEOCODE_APIKEY'],
        instance.address
    )

    RestaurantCoordinates.objects.create(
        restaurant=instance,
        longitude=restaurant_coords[0],
        latitude=restaurant_coords[1],
    )


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='ресторан',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Пункт меню ресторана'
        verbose_name_plural = 'Пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    ORDER_STATUSES = (
        ('UNPROCESSED', 'Необработанный'),
        ('PROCESSED', 'Обработанный'),
    )

    PAYMENT_METHODS = (
        ('CASH', 'Наличностью'),
        ('ELECTRONICALLY', 'Электронно'),
    )

    address = models.CharField(
        'адрес',
        max_length=255,
    )
    firstname = models.CharField(
        'имя',
        max_length=255,
    )
    lastname = models.CharField(
        'фамилия',
        max_length=255,
    )
    phonenumber = PhoneNumberField(
        'контактный телефон',
    )
    status = models.CharField(
        'статус',
        max_length=11,
        choices=ORDER_STATUSES,
        default='UNPROCESSED',
    )
    comment = models.TextField(
        'комментарий',
        blank=True,
    )
    registered_at = models.DateTimeField(
        'оформлен',
        auto_now_add=True,
    )
    called_at = models.DateTimeField(
        'осуществлен звонок',
        null=True,
        blank=True,
    )
    delivered_at = models.DateTimeField(
        'доставлен',
        null=True,
        blank=True,
    )
    payment_method = models.CharField(
        'способ оплаты',
        max_length=14,
        choices=PAYMENT_METHODS,
        null=True,
        blank=True,
    )
    restaurant_cooking_order = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
        verbose_name='ресторан, готовящий заказ',
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ номер {self.id} оформил(а) {self.firstname} {self.lastname}'


class CertainTypeProductCostManager(models.Manager):
    def get_product_type_cost(self):
        return self.annotate(cost=F('product__price') * F('quantity'))


class ProductInSomeOrder(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_products',
        verbose_name='продукт',
    )
    quantity = models.PositiveIntegerField(
        validators=[validate_quantity],
        verbose_name='кол-во продуктов',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_products',
        verbose_name='заказ',
    )
    product_type_cost = CertainTypeProductCostManager()
    objects = models.Manager()

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'Продукт {self.product.name} относится к заказу под номером {self.order.id}'




