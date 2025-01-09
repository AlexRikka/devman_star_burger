import phonenumbers

from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.serializers import ValidationError
from rest_framework.serializers import ModelSerializer, ListField

from .models import Product, Order, OrderItem
#from .serializers import OrderSerializer


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


class OrderSerializer(ModelSerializer):
    products = ListField(allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'address', 'products']

    def phonenumber_type(self, value):
        if not phonenumbers.parse(value, 'RU'):
            raise ValidationError('Wrong value')
        phonenumber = phonenumbers.parse(value, 'RU')
        if not phonenumbers.is_valid_number(phonenumber):
            raise ValidationError('Wrong format')
        phonenumber = phonenumbers.format_number(
            phonenumber, phonenumbers.PhoneNumberFormat.E164)

        return phonenumber


# @api_view(['POST'])
# def register_order(request):
#     err_content = None
#     product_id = None

#     data = request.data
#     serializer = OrderSerializer(data=data)
#     serializer.is_valid(raise_exception=True)

#     try:
#         new_order = Order.objects.create(firstname=data['firstname'],
#                                         lastname=data['lastname'],
#                                         phonenumber=data['phonenumber'],
#                                         address=data['address'])

#         for product in data['products']:
#             product_id = product['product']
#             order_item = get_object_or_404(
#                 Product, id=product_id)
#             OrderItem.objects.create(order=new_order,
#                                     product=order_item,
#                                     quantity=product['quantity'])

#     except Http404:
#         err_content = {
#             'error': f'products: invalid id {product_id}'} \
#             if not err_content else err_content
#         return Response(err_content, status=status.HTTP_404_NOT_FOUND)
    
#     return JsonResponse(data)


def order_list_api(request):
    if request.method == 'GET':
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            #serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


def order_detail_api(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = OrderSerializer(order, data=data)
        if serializer.is_valid():
            #serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        order.delete()
        return HttpResponse(status=204)
