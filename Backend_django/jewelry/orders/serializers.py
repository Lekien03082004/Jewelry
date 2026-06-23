from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_main_image=serializers.ImageField(source='product.main_image', read_only=True)
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_main_image', 'subtotal', 'price']
        read_only_fields = ['price']
        
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'status', 'status_display', 'total_price', 
            'shipping_address', 'phone','order_items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_code', 'total_price', 'status', 'created_at', 'updated_at']
        
class CreateOrderSerializer(serializers.Serializer):
    "Tạo order từ cart hiện tại"
    shipping_address = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=15)
    
    def validate_phone(self, value):
        if not value.replace('+', '').isdigit():
            raise serializers.ValidationError('Số điện thoại không hợp lê.')
        return value
    

class UpdateOrderStatusSerializer(serializers.Serializer):
    # Chỉ validate status input từ admin
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES.choices)