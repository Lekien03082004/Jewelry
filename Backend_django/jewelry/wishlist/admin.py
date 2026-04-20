from django.contrib import admin
from .models import Wishlist
# Register your models here.

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'product_id', 'created_at')
    search_fields = ('user_id', 'product_id')
    list_filter = ('created_at',)
    
admin.site.register(Wishlist, WishlistAdmin)