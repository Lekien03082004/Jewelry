from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1 #1 dòng trống thêm mới


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id')
    search_fields = ('user_id__username',)
    inlines = [CartItemInline]

@admin.register(CartItem)    
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product_id', 'quantity', 'created_at')
    list_filter = ('created_at',)
    ordering = ['-created_at']
    


admin.site.register(Cart, CartAdmin)