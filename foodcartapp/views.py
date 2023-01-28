from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .models import Order
from .models import ProductInSomeOrder
from .serializers import OrderSerializer


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
    serialized_current_order = OrderSerializer(data=request.data)
    serialized_current_order.is_valid(raise_exception=True)

    current_order = Order.objects.create(
        address=serialized_current_order.validated_data['address'],
        firstname=serialized_current_order.validated_data['firstname'],
        lastname=serialized_current_order.validated_data['lastname'],
        phonenumber=serialized_current_order.validated_data['phonenumber']
    )

    current_order_list = []
    for product in serialized_current_order.validated_data['products']:
        current_order_list.append(
            ProductInSomeOrder(
                product=product['product'],
                quantity=product['quantity'],
                order=current_order
            )
        )

    ProductInSomeOrder.objects.bulk_create(current_order_list)

    serialized_current_order_json = serialized_current_order.data
    serialized_current_order_json['id'] = current_order.id

    return Response(serialized_current_order_json, status=status.HTTP_200_OK)
