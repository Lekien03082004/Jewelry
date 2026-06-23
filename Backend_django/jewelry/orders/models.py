from django.db import models

# Create your models here.

class Order(models.Model):
    class STATUS_CHOICES(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELED = 'canceled', 'Canceled'
    user = models.ForeignKey('account.CustomerUser', on_delete=models.CASCADE, related_name="orders")
    order_code = models.CharField(max_length=20, unique=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES.PENDING)
    shipping_address = models.CharField(max_length=255)
    phone= models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('my_jewelry.Product', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    
    @property
    def subtotal(self):
        return self.quantity * self.price