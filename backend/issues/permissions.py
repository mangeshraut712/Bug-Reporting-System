"""
Custom permissions for issues app.
"""
from rest_framework import permissions


class IsReporterOrAssignee(permissions.BasePermission):
    """
    Custom permission to check if user is the reporter or assignee of an issue.
    Staff may also moderate an issue.
    """
    message = 'You do not have permission to perform this action.'

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the reporter or assignee of the issue.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return obj.reporter_id == user.id or (
            obj.assignee_id is not None and obj.assignee_id == user.id
        )
