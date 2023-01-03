from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Order, ProductsInOrder


class ProductsInOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsInOrder
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(
        child=ProductsInOrderSerializer(),
        write_only=True
    )

    class Meta:
        model = Order
        fields = ['id', 'address', 'firstname', 'lastname',
                  'phonenumber', 'products', 'status', 'comment']

    def validate_products(self, products):
        if not products:
            raise ValidationError('Этот список не может быть пустым')
        return products
