# apps/authentication/permissions.py
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Permission class for admin users only"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin
        )

class IsFarmerUser(permissions.BasePermission):
    """Permission class for farmer users"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_farmer
        )

class CanAccessFarm(permissions.BasePermission):
    """Permission to check if user can access specific farm data"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        
        # Check if object has farm attribute
        if hasattr(obj, 'farm'):
            return request.user.can_access_farm(obj.farm)
        
        # If object is a farm itself
        if hasattr(obj, 'farmers'):
            return request.user.can_access_farm(obj)
        
        return False