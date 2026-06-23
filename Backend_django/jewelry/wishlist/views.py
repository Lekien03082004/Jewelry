from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Wishlist
from .serializers import WishlistSerializer


# Create your views here.
class WishlitsView(viewsets.ModelViewSet):
    serializer_class=WishlistSerializer
    permission_classes=[IsAuthenticated]
    http_method_names=['get', 'post', 'delete']
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response(
                {
                    'detail': 'product_id là bắt buộc.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        item = Wishlist.objects.filter(user = request.user, 
                                       product_id=product_id).first()
        
        if item:
            item.delete()
            return Response({'action': 'removed'}, status=status.HTTP_200_OK)
        
        from django.shortcuts import get_object_or_404
        from my_jewelry.models import Product
        product = get_object_or_404(Product, pk=product_id)
        Wishlist.objects.create(user=request.user, product=product)
        return Response({'action': 'added'}, status=status.HTTP_201_CREATED)