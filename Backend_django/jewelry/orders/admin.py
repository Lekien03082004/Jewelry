from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'total_price', 'status', 'shipping_address', 'phone','created_at')
    search_fields = ('user_id',)
    list_filter = ('status', 'created_at')
admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'product_id', 'quantity', 'price')
    search_fields = ('order_id', 'product_id')
admin.site.register(OrderItem, OrderItemAdmin)