from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, AdminOrderViewSet
router = DefaultRouter()
router.register('', OrderViewSet, basename='order')
router.register(r'admin-order', AdminOrderViewSet, basename='admin-order')

urlpatterns = [
    path('', include(router.urls))
]
