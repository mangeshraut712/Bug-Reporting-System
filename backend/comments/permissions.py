"""Permissions for comments."""
from rest_framework import permissions


class IsCommentAuthor(permissions.BasePermission):
    """The author, the project owner, or staff may change a comment."""

    message = 'You do not have permission to perform this action.'

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        if obj.author_id == user.id:
            return True
        return obj.issue.project.created_by_id == user.id
