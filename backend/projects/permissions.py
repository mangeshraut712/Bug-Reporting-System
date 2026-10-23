"""Permissions for projects."""
from rest_framework import permissions


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """Authenticated users may read projects. Only the creator or staff may change them."""

    message = 'You do not have permission to perform this action.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return obj.created_by_id == user.id
