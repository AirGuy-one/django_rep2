from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
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
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


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
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
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
        validators=[MinValueValidator(0)]
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
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

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
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
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
        max_length=255
    )
    firstname = models.CharField(
        'имя',
        max_length=255
    )
    lastname = models.CharField(
        'фамилия',
        max_length=255
    )
    phonenumber = PhoneNumberField(
        'контактный телефон',
    )
    status = models.CharField(
        'статус',
        max_length=11,
        choices=ORDER_STATUSES,
        default='UNPROCESSED'
    )
    comment = models.TextField(
        'комментарий',
        default='',
        blank=True
    )
    registered = models.DateTimeField(
        'оформлен',
        auto_now_add=True
    )
    called = models.DateTimeField(
        'осуществлен звонок',
        null=True,
        blank=True
    )
    delivered = models.DateTimeField(
        'доставлен',
        null=True,
        blank=True
    )
    payment_method = models.CharField(
        'способ оплаты',
        max_length=14,
        choices=PAYMENT_METHODS
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='ресторан',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ номер {self.id} оформил(а) {self.firstname} {self.lastname}'


class ProductInSomeOrder(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='продукт'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='кол-во продуктов'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products'
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'Продукт {self.product.name} относится к заказу под номером {self.order.id}'
