"""
Views for comments app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Comment
from .serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
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
        queryset = Comment.objects.select_related('author', 'issue')
        
        # Filter by issue if issue_id is provided
        issue_id = self.request.query_params.get('issue_id')
        if issue_id:
            queryset = queryset.filter(issue_id=issue_id)
        
        return queryset

    def perform_create(self, serializer):
        """
        Set the author field to the current user.
        """
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['post'], url_path='create-for-issue/(?P<issue_id>[^/.]+)')
    def create_for_issue(self, request, issue_id=None):
        """
        Create a comment for a specific issue.
        """
        from issues.models import Issue
        issue = get_object_or_404(Issue, pk=issue_id)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, issue=issue)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
