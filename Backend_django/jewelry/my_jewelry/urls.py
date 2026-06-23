from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet #,ProductImageViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = router.urls
# urlpatterns += [
#     path(
#         'products/<int:product_id>/images/',
#         ProductImageViewSet.as_view({
#             'get': 'list',
#             'post': 'create'
#         })
#     ),
# ]