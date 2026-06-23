
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .serializers import CategorySerializer, ProductWriteSerializer, ProductListSerializer, ProductDetailSerializer
from .models import Product, Category
from .pagination import StandardResultsPagination


# Create your views here.
class ProductViewSet(ModelViewSet):
    # serializer_class = ProductSerializer
    lookup_field = 'slug'
    
    pagination_class = StandardResultsPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
    'category_id': ['exact'],
    'price': ['gte', 'lte'],
    }
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'price']
    ordering = ['-created_at']  
    
    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related('images').order_by('-created_at')

    
    def get_serializer_class(self):
        if self.action in ['list']:
            return ProductListSerializer
        elif self.action in ['retrieve']:
            return ProductDetailSerializer
        return ProductWriteSerializer
    
    def perform_create(self, serializer):
        product = serializer.save()

    def perform_update(self, serializer):
        product = serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # ProductImage sẽ tự xóa file nhờ Mixin
        # vì CASCADE delete gọi .delete() từng instance
        # Tuy nhiên bulk QuerySet.delete() thì KHÔNG gọi .delete()
        # nên cần xóa thủ công
        instance.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('name')
    lookup_field = 'slug'
    
# class ProductImageViewSet(ModelViewSet):
#     serializer_class = ProductImageSerializer

#     def get_queryset(self):
#         return ProductImage.objects.filter(product_id=self.kwargs['product_id'])

#     def create(self, request, *args, **kwargs):
#         product_id = self.kwargs['product_id']
#         files = request.FILES.getlist('images')

#         if not files:
#             return Response({"error": "No images"}, status=400)

#         images = []
#         for file in files:
#             images.append(
#                 ProductImage(product_id=product_id, image=file)
#             )

#         ProductImage.objects.bulk_create(images)

#         serializer = self.get_serializer(images, many=True)
#         return Response(serializer.data, status=201)