from django.urls import path
from . import views
urlpatterns = [
    path('', views.CartView.as_view(), name='cart-detail'),
    path('items/', views.CartItemAddView.as_view(), name='cart-item-add'),
    path('items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    path("clear_cart/", views.CartClearView.as_view(), name="cart_clear")
]
