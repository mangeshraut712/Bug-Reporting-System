"""
Custom permissions for issues app.
"""
from rest_framework import permissions


class IsReporterOrAssignee(permissions.BasePermission):
    """
    Reporter, assignee, the owning project's creator, or staff may change an issue.
    """
    message = 'You do not have permission to perform this action.'

    def has_object_permission(self, request, view, obj):
        """Allow the people responsible for the issue or its project."""
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        if obj.reporter_id == user.id:
            return True
        if obj.assignee_id is not None and obj.assignee_id == user.id:
            return True
        return obj.project.created_by_id == user.id
