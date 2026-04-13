from rest_framework import serializers
from .models import CustomerUser
from pyexpat import model
from dataclasses import fields

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'address', 'profile_picture']
        

