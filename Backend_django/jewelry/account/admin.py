from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomerUser
# Register your models here.

class CustomerUserAdmin(UserAdmin):
    model = CustomerUser
    list_display = ['username', 'last_name', 'first_name', 'email', 'role', 'phone_number', 'address', 'updated_at']
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {
            "fields": ("role", "phone_number", "address", "profile_picture")
        }),
    )

admin.site.register(CustomerUser, CustomerUserAdmin)