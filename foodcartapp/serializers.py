from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.serializers import ListField, IntegerField
from phonenumber_field.modelfields import PhoneNumberField
from .models import Order


class ProductsSerializer(Serializer):
    product = IntegerField()
    quantity = IntegerField()


class OrderSerializer(ModelSerializer):
    products = ListField(child=ProductsSerializer(),
                         allow_empty=False, write_only=True)
    phonenumber = PhoneNumberField()

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname',
                  'address', 'phonenumber', 'products']
