"""
Views for projects app.
"""
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from bug_tracking.mixins import PositiveIntLookupMixin
from issues.filters import filter_issues
from issues.serializers import IssueSerializer

from .models import Project
from .permissions import IsProjectOwnerOrReadOnly
from .serializers import ProjectSerializer


class ProjectViewSet(PositiveIntLookupMixin, ModelViewSet):
    """
    ViewSet for Project model.
    Provides CRUD operations for projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrReadOnly]

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
        issues = filter_issues(project.issues.all(), request.query_params)
        issues = issues.select_related('reporter', 'assignee').prefetch_related('comments')
        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)
