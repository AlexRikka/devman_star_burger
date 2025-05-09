from django.shortcuts import get_object_or_404
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError
from rest_framework.serializers import IntegerField


from .models import Order, OrderItem, Product


class ProductsSerializer(Serializer):
    product = IntegerField()
    quantity = IntegerField()

    def validate_quantity(self, value):
        if value <= 0:
            raise ValidationError("Quantity must be greater than 0.")
        return value


class OrderSerializer(ModelSerializer):
    products = ProductsSerializer(many=True,
                                  write_only=True,
                                  allow_empty=False)
    phonenumber = PhoneNumberField()

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname',
                  'address', 'phonenumber', 'products']

    def create(self, validated_data):
        order_items = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        for order_item in order_items:
            product_id = order_item['product']
            quantity = order_item['quantity']
            product = get_object_or_404(
                Product, id=product_id)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_fixed=product.price
            )

        return order
