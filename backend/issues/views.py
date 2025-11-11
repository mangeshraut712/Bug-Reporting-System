"""
Views for issues app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Issue
from .serializers import IssueSerializer
from .permissions import IsReporterOrAssignee


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Issue model.
    Provides CRUD operations for issues.
    """
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optimize queries using select_related and prefetch_related.
        """
        queryset = Issue.objects.select_related('project', 'reporter', 'assignee').prefetch_related('comments')
        
        # Filter by project if project_id is provided
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset

    def perform_create(self, serializer):
        """
        Set the reporter field to the current user.
        """
        serializer.save(reporter=self.request.user)

    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action == 'partial_update' or self.action == 'update':
            return [IsAuthenticated(), IsReporterOrAssignee()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='create-for-project/(?P<project_id>[^/.]+)')
    def create_for_project(self, request, project_id=None):
        """
        Create an issue for a specific project.
        """
        from projects.models import Project
        project = get_object_or_404(Project, pk=project_id)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user, project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update the status of an issue.
        """
        issue = self.get_object()
        self.check_object_permissions(request, issue)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response({'error': 'Status is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        issue.status = new_status
        issue.save()
        serializer = self.get_serializer(issue)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        """
        Assign an issue to a user.
        """
        issue = self.get_object()
        self.check_object_permissions(request, issue)
        
        assignee_id = request.data.get('assignee_id')
        if not assignee_id:
            issue.assignee = None
        else:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                assignee = User.objects.get(pk=assignee_id)
                issue.assignee = assignee
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        issue.save()
        serializer = self.get_serializer(issue)
        return Response(serializer.data)
