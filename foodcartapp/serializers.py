from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Order, ProductInSomeOrder


class ProductsInOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInSomeOrder
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(
        child=ProductsInOrderSerializer(),
        write_only=True,
        allow_empty=False,
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'address',
            'firstname',
            'lastname',
            'phonenumber',
            'status',
            'comment',
            'registered_at',
            'called_at',
            'delivered_at',
            'payment_method',
            'restaurant',
            'products',
        ]

    def validate_products(self, products):
        if not products:
            raise ValidationError('Этот список не может быть пустым')
        return products
