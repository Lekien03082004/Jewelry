from django.db import models

# Create your models here.

class Review(models.Model):
    user_id = models.ForeignKey('account.CustomerUser', on_delete=models.CASCADE, related_name='reviews')
    product_id = models.ForeignKey('my_jewelry.Product', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)