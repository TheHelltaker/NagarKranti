from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsMunicipalOrReadOnly(BasePermission):
    """
    Custom permission:
      - Read-only methods are allowed for any authenticated user.
      - Only municipal-type users can update (PUT/PATCH/DELETE).
      - Citizens can only POST (create) new issues.
    """
    def has_permission(self, request, view):
        # Allow safe methods for any authenticated user.
        if request.method in SAFE_METHODS:
            return True

        # Allow POST (create) for citizens.
        if request.method == 'POST' and request.user.type == 'CITIZEN':
            return True

        # For methods that modify (PUT, PATCH, DELETE) require municipal type.
        if request.method not in SAFE_METHODS and request.user.type == 'MUNICIPAL':
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # Object-level permissions: allow safe methods for everyone.
        if request.method in SAFE_METHODS:
            return True

        # Only municipal users can update any object.
        return request.user.type == 'MUNICIPAL'

class IsMunicipalUser(BasePermission):
    """
    Allows access only to users with type 'MUNICIPAL'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == 'MUNICIPAL'