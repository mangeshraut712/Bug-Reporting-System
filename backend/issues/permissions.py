"""
Custom permissions for issues app.
"""
from rest_framework import permissions


class IsReporterOrAssignee(permissions.BasePermission):
    """
    Custom permission to check if user is the reporter or assignee of an issue.
    """
    message = 'You do not have permission to perform this action.'

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the reporter or assignee of the issue.
        """
        return obj.reporter == request.user or obj.assignee == request.user
