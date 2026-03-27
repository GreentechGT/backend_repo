from rest_framework import permissions

class IsVendor(permissions.BasePermission):
    """
    Allows access only to users with the 'vendor' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'vendor')

class IsCustomer(permissions.BasePermission):
    """
    Allows access only to users with the 'customer' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'customer')
