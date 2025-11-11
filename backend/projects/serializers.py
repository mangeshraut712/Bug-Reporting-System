"""
Serializers for projects app.
"""
from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    issue_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'created_by', 'created_by_name', 'created_at', 'updated_at', 'issue_count')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def get_issue_count(self, obj):
        """
        Get the count of issues for this project.
        """
        return obj.issues.count()
