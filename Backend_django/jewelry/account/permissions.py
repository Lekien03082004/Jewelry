from rest_framework.permissions import BasePermission

class IsCustomer(BasePermission):
    message = 'Chỉ khách hàng mới có thể thực hiện hành động này.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'customer')
    
class IsManager(BasePermission):
    message = 'Chỉ quản lý mới có thể thực hiện hành động này.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'manager')
    
class IsAdminRole(BasePermission):
    # Phân biệt với IsAdminUser của DRF (dựa vào is_staff).
    message = 'Chỉ amdin mới có thể thực hiện hành động này.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')
    
class IsAdminOrManager(BasePermission):
    # Phân biệt với IsAdminUser của DRF (dựa vào is_staff).
    message = 'Chỉ amdin hoặc manager mới có thể thực hiện hành động này.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ('admin', 'manager'))
    
