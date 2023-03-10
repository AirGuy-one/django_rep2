import os

from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError

from restaurateur.fetch_coordinates import fetch_coordinates
from .models import Product, RestaurantCoordinates
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order
from .models import ProductInSomeOrder


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]

    @receiver(post_save, sender=Restaurant)
    def update_stock(sender, instance, **kwargs):
        restaurant_coords = fetch_coordinates(
            os.environ['GEOCODE_APIKEY'],
            instance.address
        )
        if restaurant_coords is None:
            raise ValidationError('restaurant_coords have not found')

        longitude, latitude = restaurant_coords

        RestaurantCoordinates.objects.create(
            restaurant=instance,
            longitude=longitude,
            latitude=latitude,
        )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('??????????', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('????????????????', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return '???????????????? ????????????????'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = '????????????'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return '?????? ????????????????'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = '????????????'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


class ProductsInOrderInline(admin.TabularInline):
    model = ProductInSomeOrder
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'firstname',
        'lastname',
        'address',
        'phonenumber'
    ]
    list_display = [
        'firstname',
        'lastname',
        'address',
        'phonenumber'
    ]
    readonly_fields = [
        'registered_at'
    ]
    inlines = [
        ProductsInOrderInline,
    ]

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if "next" in request.GET:
            return HttpResponseRedirect(request.GET['next'])
        else:
            return res
