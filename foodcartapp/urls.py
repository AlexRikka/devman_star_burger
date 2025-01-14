from django.urls import path

from .views import product_list_api, banners_list_api , register_order
#from .views import order_detail_api, order_list_api

app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('banners/', banners_list_api),
    path('order/', register_order),
    #path('orders/', order_list_api),
    #path('orders/<int:pk>/', order_detail_api),
]
