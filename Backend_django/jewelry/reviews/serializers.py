from rest_framework import serializers
from account.models import CustomerUser
from .models import Review

class ReviewUserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = ['id', 'full_name']
        

class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserMiniSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate_rating(self, value):
        if not (1<= value <=5):
            raise serializers.ValidationError("Rating phải từ 1 đến 5.")
        return value

