
from django.urls import path
from .views import ListUserApi

urlpatterns = [
    path('users/', ListUserApi.as_view(), name='list-users'),
]
