from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class Review(models.Model):
    user = models.ForeignKey('account.CustomerUser', on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey('my_jewelry.Product', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_active'])
        ]
        
    def __str__(self):
        return f'{self.user} - {self.product} - {self.rating}.'