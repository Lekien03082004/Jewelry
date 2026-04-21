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
        fields=['username','first_name','last_name', 'email','phone_number', 'password', 'confirm_password']
        
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required")

        if CustomerUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")

        return value
    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("PHone number is required")
        if CustomerUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists")
        
        return value
    
    def validate(self, data):
        
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password":"Passwords do not match"})
        
        validate_password(data["password"])
        return data
    
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        print(validated_data)
        return CustomerUser.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise serializers.ValidationError("Invalid credentials")

        data["username"] = username.strip().lower()
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'address', 'profile_picture']
        
