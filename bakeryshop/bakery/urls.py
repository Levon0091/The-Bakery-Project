from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('product/<int:product_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('order/success/', views.order_success, name='order_success'),
    path('order/error/', views.order_error, name='order_error'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/<int:order_id>/pay/', views.pay_order, name='pay_order'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('orders/<int:order_id>/continue_payment/', views.continue_payment, name='continue_payment'),
    path('orders/<int:order_id>/cancel_unpaid/', views.cancel_order, name='cancel_unpaid_order'),
    path('orders/<int:order_id>/refund/', views.request_refund, name='request_refund'),
    path('change-lang/<str:lang>/', views.change_language, name='change_language'),
]


