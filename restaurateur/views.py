from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, F, Sum
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.db import transaction
from django.conf import settings
from geopy import distance

from foodcartapp.models import Product
from foodcartapp.models import Restaurant
from foodcartapp.models import Order
from foodcartapp.serializers import OrderSerializer
from .fetch_coordinates import fetch_coordinates


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items').select_related('category'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@transaction.atomic
@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    products_in_restaurants = {}

    for restaurant in Restaurant.objects.prefetch_related('menu_items__product').all():
        products = [menu_item.product for menu_item in restaurant.menu_items.all()]

        products_in_restaurants[restaurant] = products

    serialized_orders = OrderSerializer(Order.objects.all().select_related('restaurant_cooking'), many=True).data

    for order_number, order in enumerate(Order.objects.filter(status='UNPROCESSED').prefetch_related(
        Prefetch(
            'order_products__product',
        ),
    ).annotate(cost=Sum(F('order_products__price')))):

        list_products = []

        for product in order.order_products.all():
            list_products.append(product.product)

        serialized_orders[order_number].update(
            {
                'cost': order.cost if order.cost is not None else 0,
                'status': order.get_status_display(),
                'payment_method': order.get_payment_method_display(),
                'restaurant': order.restaurant_cooking
            }
        )

        customer_coords = fetch_coordinates(settings.GEOCODE_API_KEY, order.address)
        if customer_coords is None:
            raise ValidationError('customer_coords have not found')

        restaurants_can_fulfill_order = []

        for restaurant_address_index, restaurant in enumerate(products_in_restaurants):
            products_in_restaurant = products_in_restaurants[restaurant]
            if set(list_products).issubset(products_in_restaurant):
                restaurant_coords = (
                    restaurant.latitude,
                    restaurant.longitude
                )

                restaurant_distance_pair = {
                    'restaurant': restaurant.name,
                    'distance': str(distance.distance(restaurant_coords,
                                                      customer_coords).miles)[:-10]
                }

                restaurants_can_fulfill_order.append(restaurant_distance_pair)

        serialized_orders[order_number]['restaurants_can_fulfill_order'] = restaurants_can_fulfill_order

    return render(request, template_name='order_items.html', context={
        'orders': serialized_orders,
    })
