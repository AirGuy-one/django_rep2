import os

from django import forms
from django.db.models import Prefetch, Sum
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.db import transaction
from geopy import distance
from dotenv import load_dotenv

from foodcartapp.models import Product, ProductInSomeOrder, RestaurantMenuItem, RestaurantCoordinates
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
    load_dotenv()

    apikey = os.environ['GEOCODE_APIKEY']

    products_in_restaurants = {}

    for restaurant in Restaurant.objects.prefetch_related(
        Prefetch(
            'menu_items__product',
            queryset=RestaurantMenuItem.objects.all().only('product')
        )
    ).all().only('name'):
        products = []
        for menu_item in restaurant.menu_items.all():
            products.append(menu_item.product.product)
        # products = [menu_item.product.product for menu_item in restaurant.menu_items.all()]
        products_in_restaurants[restaurant.name] = products

    serialized_orders = OrderSerializer(Order.objects.all().select_related('restaurant_cooking_order'), many=True).data
    order_number = 0

    restaurants_addresses = list(RestaurantCoordinates.objects.all())

    for order in Order.objects.prefetch_related(
        Prefetch(
            'products_in_some_order__product',
        ),
    ).all():
        list_products = []

        for product in order.products_in_some_order.all():
            list_products.append(product.product)

        cost = order.products_in_some_order.get_product_type_cost().aggregate(
            total_cost=Sum('cost')
        )['total_cost']

        if cost is None:
            cost = 0

        serialized_orders[order_number]['cost'] = cost
        serialized_orders[order_number]['status'] = order.get_status_display()
        serialized_orders[order_number]['payment_method'] = order.get_payment_method_display()
        serialized_orders[order_number]['restaurant'] = order.restaurant_cooking_order

        customer_coords = fetch_coordinates(apikey, order.address)

        restaurants_can_fulfill_order = []

        restaurant_address_index = 0

        for name_of_restaurant, products_in_restaurant in products_in_restaurants.items():
            if set(list_products).issubset(products_in_restaurant):
                restaurant_coords = (
                    restaurants_addresses[restaurant_address_index].latitude,
                    restaurants_addresses[restaurant_address_index].longitude
                )

                restaurant_distance_pair = {
                    'restaurant': name_of_restaurant,
                    'distance': str(distance.distance(restaurant_coords,
                                                      customer_coords).miles)[:-10]
                }

                restaurants_can_fulfill_order.append(restaurant_distance_pair)

            restaurant_address_index += 1

        serialized_orders[order_number]['restaurants_can_fulfill_order'] = restaurants_can_fulfill_order

        order_number += 1

    return render(request, template_name='order_items.html', context={
        'orders': serialized_orders,
    })
