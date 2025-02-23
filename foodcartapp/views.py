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


class ProductsSerializer(Serializer):
    product = IntegerField()
    quantity = IntegerField()


class OrderSerializer(ModelSerializer):
    products = ListField(child=ProductsSerializer(),
                         allow_empty=False, write_only=True)
    phonenumber = CharField()

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname',
                  'address', 'phonenumber', 'products']

    def validate_phonenumber(self, value):
        if not phonenumbers.parse(value, 'RU'):
            raise ValidationError('Wrong value')
        phonenumber = phonenumbers.parse(value, 'RU')
        if not phonenumbers.is_valid_number(phonenumber):
            raise ValidationError('Wrong format')
        phonenumber_formatted = phonenumbers.format_number(
            phonenumber, phonenumbers.PhoneNumberFormat.E164)

        return phonenumber_formatted


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    err_content = None
    product_id = None

    data = request.data
    serializer = OrderSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    try:
        new_order = Order.objects.create(
            firstname=serializer.validated_data['firstname'],
            lastname=serializer.validated_data['lastname'],
            phonenumber=serializer.validated_data['phonenumber'],
            address=serializer.validated_data['address'],
            status='proc')

        for product in serializer.validated_data['products']:
            product_id = product['product']
            product_item = get_object_or_404(
                Product, id=product_id)
            OrderItem.objects.create(order=new_order,
                                     product=product_item,
                                     quantity=product['quantity'],
                                     price_fixed=product_item.price)

    except Http404:
        err_content = {
            'error': f'products: invalid id {product_id}'} \
            if not err_content else err_content
        return Response(err_content, status=status.HTTP_404_NOT_FOUND)

    new_order_serialized = OrderSerializer(new_order)

    return Response(new_order_serialized.data)
