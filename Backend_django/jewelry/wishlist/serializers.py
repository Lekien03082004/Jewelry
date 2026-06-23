
from rest_framework import serializers
from my_jewelry.models import Product
from .models import Wishlist
from cart.serializers import ProductMiniSerializer

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductMiniSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_id', 'created_at']
        
    def validate(self, attrs):
        request= self.context['request']
        product = attrs.get('product')
        if Wishlist.objects.filter(user=request.user, product=product, ).exists():
            raise serializers.ValidationError({'detail':'Sản phẩm đã có trong wishlist'})
        return attrs
    
    def create(self, vaildate_data):
        vaildate_data['user'] = self.context['request'].user
        return super().create(vaildate_data)
        