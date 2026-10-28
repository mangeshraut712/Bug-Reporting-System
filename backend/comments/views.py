"""
Views for comments app.
"""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from bug_tracking.mixins import PositiveIntLookupMixin
from bug_tracking.validation import parse_positive_int, require_object_payload
from issues.models import Issue

from .models import Comment
from .permissions import IsCommentAuthor
from .serializers import CommentSerializer


class CommentViewSet(PositiveIntLookupMixin, ModelViewSet):
    """
    ViewSet for Comment model.
    Provides CRUD operations for comments.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optimize queries using select_related.
        """
        queryset = Comment.objects.select_related('author', 'issue__project').order_by(
            'created_at', 'id'
        )
        issue_id = parse_positive_int(self.request.query_params.get('issue_id'), 'issue_id')
        if issue_id is not None:
            queryset = queryset.filter(issue_id=issue_id)
        return queryset

    def perform_create(self, serializer):
        """
        Set the author field to the current user.
        """
        serializer.save(author=self.request.user)

    def get_permissions(self):
        """Only the author or staff may edit or delete a comment."""
        if self.action in {'update', 'partial_update', 'destroy'}:
            return [IsAuthenticated(), IsCommentAuthor()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='create-for-issue/(?P<issue_id>[^/.]+)')
    def create_for_issue(self, request, issue_id=None):
        """
        Create a comment for a specific issue.
        """
        parsed_id = parse_positive_int(issue_id, 'issue_id')
        issue = get_object_or_404(Issue, pk=parsed_id)

        data = require_object_payload(request.data).copy()
        data['issue'] = issue.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, issue=issue)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
