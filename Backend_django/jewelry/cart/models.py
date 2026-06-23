from django.db import models

# Create your models here. 

class Cart(models.Model):
    user = models.OneToOneField('account.CustomerUser', on_delete=models.CASCADE, related_name='carts')
    


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('my_jewelry.Product', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['-created_at']