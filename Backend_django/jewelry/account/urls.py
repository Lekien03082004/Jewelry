
from django.urls import path
from .views import ListUserApi, LoginView, Logout

urlpatterns = [
    
    path('logout/', Logout.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', ListUserApi.as_view(), name='list-users'),
]
