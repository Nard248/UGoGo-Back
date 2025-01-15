from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows only the owner of an object to modify it.
    Assumes the model instance has a `user` attribute for ownership.
    """
    def has_object_permission(self, request, view, obj):
        # Safe methods (GET, HEAD, OPTIONS) are always allowed
        if request.method in permissions.SAFE_METHODS:
            return True
        # Otherwise, must be the owner
        return getattr(obj, 'user', None) == request.user


class IsCourierOfOffer(permissions.BasePermission):
    """
    Allows only the courier (offer.courier) to update the request status.
    """
    def has_object_permission(self, request, view, obj):
        # Safe methods are allowed
        if request.method in permissions.SAFE_METHODS:
            return True
        # For write operations, must be the courier
        return getattr(obj.offer, 'courier', None) == request.user
