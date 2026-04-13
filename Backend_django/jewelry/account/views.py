from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import CustomerUser
from .serializers import UserSerializer 
# Create your views here.


class ListUserApi(ListAPIView):
    queryset = CustomerUser.objects.all()
    serializer_class = UserSerializer