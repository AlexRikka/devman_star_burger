from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order


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
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(
            restaurant.id, False) for restaurant in restaurants]

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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    products = Product.objects.available().prefetch_related('menu_items')
    orders = Order.objects.exclude(
        status='end').price().prefetch_related('order_items').order_by('-status')   #('-created_at')

    orders_with_restaurant_availability = []

    for order in orders:
        if order.status == 'proc':
            order_products_raw = [
                item.product.id for item in order.order_items.all()]
            order_products = list(products.filter(
                pk__in=order_products_raw).all())

            products_with_restaurants = []
            for product in order_products:
                restaurant_ids = [
                    item.restaurant_id for item in product.menu_items.all()]

                products_with_restaurants.append({
                    'product': product,
                    'restaurant_ids': restaurant_ids
                })

            if products_with_restaurants:
                common_restaurant_ids = products_with_restaurants[0]['restaurant_ids']
                for i in range(1, len(products_with_restaurants)):
                    common_restaurant_ids = [id for id in common_restaurant_ids[i]
                                             ['restaurant_ids'] if id in common_restaurant_ids[i-1]['restaurant_ids']]

                orders_with_restaurant_availability.append({
                    'order': order,
                    'restaurants': list(Restaurant.objects.filter(id__in=common_restaurant_ids).all()),
                    'proc': order.status == 'proc'
                })
            else:
                orders_with_restaurant_availability.append({
                    'order': order,
                    'restaurants': None,
                    'proc': True
                })
        else:
            orders_with_restaurant_availability.append({
                'order': order,
                'restaurants': order.restaurant,
                'proc': False
            })

    return render(request, template_name='order_items.html', context={
        'order_items': orders_with_restaurant_availability
    })
