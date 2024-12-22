from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderItem


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
    err_content = None
    try:
        data = request.data

        if 'products' not in data.keys():
            err_content = {
                'error': 'Products key is not presented'}
            raise KeyError()

        if not isinstance(data['products'], list):
            err_content = {
                'error': 'Products key is not list'}
            raise TypeError()

        if not data['products']:
            err_content = {
                'error': 'Products list is empty'}
            raise ValueError()

        new_order = Order.objects.create(firstname=data['firstname'],
                                         lastname=data['lastname'],
                                         phonenumber=data['phonenumber'],
                                         address=data['address'])

        for product in data['products']:
            order_item = get_object_or_404(
                Product, id=product['product'])
            OrderItem.objects.create(order=new_order,
                                     product=order_item,
                                     quantity=product['quantity'])

    except ValueError:
        err_content = {
            'error': 'Error register request'} if not err_content else err_content
        return Response(err_content, status=status.HTTP_404_NOT_FOUND)
    except KeyError:
        err_content = {
            'error': 'Invalid field set'} if not err_content else err_content
        return Response(err_content, status=status.HTTP_404_NOT_FOUND)
    except TypeError:
        err_content = {
            'error': 'Invalid field type'} if not err_content else err_content
        return Response(err_content, status=status.HTTP_404_NOT_FOUND)

    return JsonResponse(data)
