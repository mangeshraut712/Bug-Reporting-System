"""
Serializers for issues app.
"""
from rest_framework import serializers
from .models import Issue


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for Issue model.
    """
    reporter_name = serializers.CharField(source='reporter.get_full_name', read_only=True)
    assignee_name = serializers.CharField(source='assignee.get_full_name', read_only=True, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'description', 'status', 'priority', 'project', 'project_name',
            'reporter', 'reporter_name', 'assignee', 'assignee_name', 'created_at', 'updated_at', 'comment_count'
        )
        read_only_fields = ('id', 'reporter', 'created_at', 'updated_at')

    def get_comment_count(self, obj):
        """
        Get the count of comments for this issue.
        """
        return obj.comments.count()

    def validate_status(self, value):
        """
        Validate status value.
        """
        valid_statuses = [choice[0] for choice in Issue.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        return value

    def validate_priority(self, value):
        """
        Validate priority value.
        """
        valid_priorities = [choice[0] for choice in Issue.PRIORITY_CHOICES]
        if value not in valid_priorities:
            raise serializers.ValidationError(f'Invalid priority. Must be one of: {", ".join(valid_priorities)}')
        return value
