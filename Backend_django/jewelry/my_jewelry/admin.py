from django.contrib import admin

from .models import Category, Product, ProductImage

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description', 'quantity', 'category_id', 'material', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('price',)
    
admin.site.register(Product, ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

admin.site.register(Category, CategoryAdmin)

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    
admin.site.register(ProductImage, ProductImageAdmin)