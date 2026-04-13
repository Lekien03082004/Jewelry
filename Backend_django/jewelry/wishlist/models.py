from django.db import models

# Create your models here.

class Wishlist(models.Model):
    user_id = models.ForeignKey('account.CustomerUser', on_delete=models.CASCADE, related_name='wishlists')
    product_id = models.ForeignKey('my_jewelry.Product', on_delete=models.CASCADE, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)