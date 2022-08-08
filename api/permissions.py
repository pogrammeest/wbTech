from rest_framework import permissions


class IsOwnerOrAdminAccount(permissions.BasePermission):
    """
    Custom permission to only self-user allow to see and edit it.
    Admin users however have access to all.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj == request.user
