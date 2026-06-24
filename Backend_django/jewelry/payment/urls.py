from django.urls import path
from .views import VNPayIPNView, VNPayReturnView, CreatePaymentUrlView
urlpatterns = [
    path('orders/<str:order_code>/pay/', CreatePaymentUrlView.as_view(), name='create-payment'),
    path('vnpay/return/', VNPayReturnView.as_view(), name='create-payment'),
    path('vnpay/ipn/', VNPayIPNView.as_view(), name='create-payment'),
]