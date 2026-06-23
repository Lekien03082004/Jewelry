from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from .serializers import CartSerializer, CartItemSerializer

from .services import CartService
# Create your views here.

class CartView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        cart = CartService.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        
        return Response(serializer.data)
    
class CartItemAddView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get("quantity", 1))
        
        try:
            cart_item = CartService.add_item(request.user, product_id, quantity)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(
            CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )
        
class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    
    def patch(self, request, pk):
        quantity = request.data.get('quantity')
        
        if quantity is None:
            return Response({'error': 'Không tồn tại trường quantity.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart_item = CartService.update_item(request.user, pk, quantity)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(CartItemSerializer(cart_item).data)
    
    def delete(self, request, pk):
        CartService.remove_item(request.user, pk)
        return Response({"message": "Delete product in cart successfully!"},status=status.HTTP_200_OK)
    
class CartClearView(APIView):
    
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        CartService.clear_cart(request.user)
        return Response({"message": "Đã xóa toàn bộ giỏ hàng."})
        