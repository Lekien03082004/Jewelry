from django.db import models

# Create your models here. 

class Cart(models.Model):
    user_id = models.ForeignKey('account.CustomerUser', on_delete=models.CASCADE, related_name='carts')
    product_id = models.ForeignKey('my_jewelry.Product', on_delete=models.CASCADE, related_name='carts')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)