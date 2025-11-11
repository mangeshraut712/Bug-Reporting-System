"""
Views for projects app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project model.
    Provides CRUD operations for projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optimize queries using select_related and prefetch_related.
        """
        return Project.objects.select_related('created_by').prefetch_related('issues')

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def issues(self, request, pk=None):
        """
        Get all issues for a specific project.
        """
        project = self.get_object()
        issues = project.issues.all()
        
        # Apply filters
        status_filter = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        search = request.query_params.get('search')

        if status_filter:
            issues = issues.filter(status=status_filter)
        if priority_filter:
            issues = issues.filter(priority=priority_filter)
        if search:
            issues = issues.filter(title__icontains=search) | issues.filter(description__icontains=search)

        # Optimize queries
        issues = issues.select_related('reporter', 'assignee').prefetch_related('comments')

        from issues.serializers import IssueSerializer
        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)
