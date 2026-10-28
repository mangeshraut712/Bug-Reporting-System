"""
Views for issues app.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DataError
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from bug_tracking.mixins import PositiveIntLookupMixin
from bug_tracking.validation import parse_positive_int, require_object_payload
from projects.models import Project

from .filters import filter_issues
from .models import Issue
from .permissions import IsReporterOrAssignee
from .serializers import IssueSerializer

User = get_user_model()

MUTATING_ACTIONS = {'update', 'partial_update', 'destroy', 'update_status', 'assign'}


class IssueViewSet(PositiveIntLookupMixin, ModelViewSet):
    """
    ViewSet for Issue model.
    Provides CRUD operations for issues.
    """
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Load related rows and comment totals without a query per issue."""
        queryset = Issue.objects.select_related(
            'project', 'reporter', 'assignee'
        ).annotate(annotated_comment_count=Count('comments'))

        project_id = parse_positive_int(self.request.query_params.get('project_id'), 'project_id')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)

        # Count() groups rows and drops the model's default ordering, which
        # makes pagination unstable. Put the newest issues first explicitly.
        return filter_issues(queryset, self.request.query_params).order_by('-created_at', '-id')

    def perform_create(self, serializer):
        """
        Set the reporter field to the current user.
        """
        serializer.save(reporter=self.request.user)

    def get_permissions(self):
        """
        Reporter, assignee, or staff may change an issue. Other users may read it.
        """
        if self.action in MUTATING_ACTIONS:
            return [IsAuthenticated(), IsReporterOrAssignee()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='create-for-project/(?P<project_id>[^/.]+)')
    def create_for_project(self, request, project_id=None):
        """
        Create an issue for a specific project.
        """
        parsed_id = parse_positive_int(project_id, 'project_id')
        project = get_object_or_404(Project, pk=parsed_id)

        data = require_object_payload(request.data).copy()
        data['project'] = project.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reporter=request.user, project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update the status of an issue.
        """
        issue = self.get_object()
        new_status = require_object_payload(request.data).get('status')
        if new_status in (None, ''):
            return Response({'error': 'Status is required.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(issue, data={'status': new_status}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        """
        Assign an issue to a user.
        """
        issue = self.get_object()
        data = require_object_payload(request.data)
        if 'assignee_id' not in data or data.get('assignee_id') in (None, ''):
            issue.assignee = None
            issue.save()
            return Response(self.get_serializer(issue).data)

        try:
            assignee_id = parse_positive_int(data.get('assignee_id'), 'assignee_id')
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignee = User.objects.get(pk=assignee_id)
        except (User.DoesNotExist, DjangoValidationError, DataError, OverflowError, ValueError):
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not assignee.is_active:
            return Response(
                {'error': 'Inactive users cannot be assigned.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        issue.assignee = assignee
        issue.save()
        return Response(self.get_serializer(issue).data)
