"""
Chuyển object/model ↔ JSON.
Kiểm tra dữ liệu đầu vào.
Quy định các trường được trả về hoặc được phép ghi.
"""
from rest_framework import serializers
from my_jewelry.models import Product
from .models import CartItem, Cart

class ProductMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'main_image', "price"]
    
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductMiniSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    subtotal=serializers.SerializerMethodField()
    
    class Meta:
        model=CartItem
        fields= ['id', 'product', 'product_id','quantity', 'subtotal']
        
    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0.")
        return value
    
    def validate(self, data):
        product = data.get('product')
        quantity= data.get('quantity', 1)
        if product and product.quantity < quantity:
            raise serializers.ValidationError(f"Sản phẩm chỉ còn {product.quantity} trong kho!")
        
        return data
    
    
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    
    class Meta: 
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_items']
        
    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())
    
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
    