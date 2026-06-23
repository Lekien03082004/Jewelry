from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WishlitsView

router = DefaultRouter()
router.register('', WishlitsView, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
]
