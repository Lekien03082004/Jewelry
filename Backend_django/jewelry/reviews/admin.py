from django.contrib import admin
from .models import Review
# Register your models here.


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'user_id', 'rating', 'comment', 'created_at')
    list_filter = ('rating',)
    
admin.site.register(Review, ReviewAdmin)
    