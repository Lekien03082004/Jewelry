from django.db import models

# Create your models here.

class Wishlist(models.Model):
    user = models.ForeignKey('account.CustomerUser', on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey('my_jewelry.Product', on_delete=models.CASCADE, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together=('user', 'product')
        ordering=['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at'])
        ]
        
    def __str__(self):
        return f'{self.user} - {self.product}.'