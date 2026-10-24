"""
Serializers for projects app.
"""
from rest_framework import serializers

from accounts.models import user_display_name
from bug_tracking.validation import MAX_DESCRIPTION_LENGTH

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    """
    created_by_name = serializers.SerializerMethodField()
    issue_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'issue_count',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def get_created_by_name(self, obj):
        """Display name of the creator, including after that user is deleted."""
        return user_display_name(obj.created_by)

    def get_issue_count(self, obj):
        """Count issues from an annotation when the view provided one."""
        annotated = getattr(obj, 'annotated_issue_count', None)
        if annotated is not None:
            return annotated
        return obj.issues.count()

    def validate_name(self, value):
        """Reject a blank project name."""
        name = value.strip()
        if not name:
            raise serializers.ValidationError('Name cannot be blank.')
        return name

    def validate_description(self, value):
        """Reject a blank or oversized project description."""
        description = value.strip()
        if not description:
            raise serializers.ValidationError('Description cannot be blank.')
        if len(description) > MAX_DESCRIPTION_LENGTH:
            raise serializers.ValidationError('Description is too long.')
        return description
