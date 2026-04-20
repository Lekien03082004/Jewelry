from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomerUser
from pyexpat import model
from dataclasses import fields

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model=CustomerUser
        fields=['username','first_name','last_name', 'email', 'password', 'confirm_password']
        
        def validate(self, data):
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            
            if password != confirm_password:
                raise serializers.ValidationError("Passwords do not match")
            
            validate_password(password)
            
            return data
        
        def create(self, validated_data):
            
            validated_data.pop("confirm_password")
            
            user = CustomerUser(
                username=validated_data["username"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                email=validated_data.get("email", "")
            )
            
            user.set_password(validated_data["password"]) #hassh password
            user.save()
            return user

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError("Invalid credentials")

        attrs["username"] = username.strip().lower()
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'address', 'profile_picture']
        
