from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomerUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=[('customer', 'Customer'), ('manager', 'Manager'),('admin', 'Admin')], default='customer')
    phone_number = models.CharField(max_length=15,unique=True, blank=True, null=True)
    email=models.EmailField(unique=True)
    address = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username