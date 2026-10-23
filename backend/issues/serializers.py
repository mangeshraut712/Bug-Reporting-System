"""
Serializers for issues app.
"""
from rest_framework import serializers

from accounts.models import user_display_name

from .models import Issue


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for Issue model.
    """
    reporter_name = serializers.SerializerMethodField()
    assignee_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'description', 'status', 'priority', 'project', 'project_name',
            'reporter', 'reporter_name', 'assignee', 'assignee_name', 'created_at', 'updated_at',
            'comment_count',
        )
        read_only_fields = ('id', 'reporter', 'created_at', 'updated_at')

    def get_reporter_name(self, obj):
        """Display name of the reporter, or null when that user was deleted."""
        return user_display_name(obj.reporter)

    def get_assignee_name(self, obj):
        """Display name of the assignee, or null when the issue is unassigned."""
        return user_display_name(obj.assignee)

    def get_comment_count(self, obj):
        """
        Get the count of comments for this issue.
        """
        return obj.comments.count()

    def validate_title(self, value):
        """Reject a blank title."""
        title = value.strip()
        if not title:
            raise serializers.ValidationError('Title cannot be blank.')
        return title

    def validate_description(self, value):
        """Reject a blank description."""
        description = value.strip()
        if not description:
            raise serializers.ValidationError('Description cannot be blank.')
        return description

    def validate_status(self, value):
        """
        Validate status value.
        """
        valid_statuses = [choice[0] for choice in Issue.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            )
        return value

    def validate_priority(self, value):
        """
        Validate priority value.
        """
        valid_priorities = [choice[0] for choice in Issue.PRIORITY_CHOICES]
        if value not in valid_priorities:
            raise serializers.ValidationError(
                f'Invalid priority. Must be one of: {", ".join(valid_priorities)}'
            )
        return value
