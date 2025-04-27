import phonenumbers

from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.serializers import ListField, IntegerField, CharField

from .models import Product, Order, OrderItem
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


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    err_content = None
    product_id = None

    data = request.data
    serializer = OrderSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    try:
        new_order = serializer.save()

    except Http404:
        err_content = {
            'error': f'products: invalid id {product_id}'} \
            if not err_content else err_content
        return Response(err_content, status=status.HTTP_404_NOT_FOUND)

    new_order_serialized = OrderSerializer(new_order)

    return Response(new_order_serialized.data)
