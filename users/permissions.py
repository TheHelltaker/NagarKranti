from rest_framework import permissions

class IsMunicipalUser(permissions.BasePermission):
    """
    Permission check for municipal officers.
    """
    message = "Only municipal officers can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_municipal_user()

class IsOwnerOrMunicipal(permissions.BasePermission):
    """
    Permission check for:
    - Object owner (for citizen users viewing their own data)
    - Municipal users (who can view all data)
    """
    message = "You can only view your own data unless you are a municipal officer."

    def has_object_permission(self, request, view, obj):
        # Allow municipal users to access all objects
        if request.user.is_municipal_user():
            return True
            
        # Check if the object has a user field referencing the requesting user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'reported_by'):
            return obj.reported_by == request.user
            
        # If the object is a user, check if it's the requesting user
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
            
        return False