from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .models import Order
from .models import ProductsInOrder


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    if request.method == 'POST':
        order_info = request.data

        if 'address' in order_info and 'firstname' in order_info and \
            'lastname' in order_info and 'phonenumber' in order_info and \
            'products' in order_info and isinstance(order_info['address'], str) and \
            isinstance(order_info['firstname'], str) and isinstance(order_info['lastname'], str) and \
            isinstance(order_info['phonenumber'], str) and isinstance(order_info['products'], list) and \
            order_info['products']:
            current_order = Order.objects.create(
                address=order_info['address'],
                first_name=order_info['firstname'],
                last_name=order_info['lastname'],
                phone_number=order_info['phonenumber'],
            )

            for product_info in order_info['products']:
                ProductsInOrder.objects.create(
                    product=Product.objects.get(pk=product_info['product']),
                    quantity=product_info['quantity'],
                    order=current_order
                )

            return Response(request.data, status=status.HTTP_200_OK)

        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)
