"""
Tests for comments app.
"""
import pytest
from rest_framework import status
from projects.models import Project
from issues.models import Issue
from .models import Comment


@pytest.mark.django_db
class TestCommentEndpoints:
    """
    Test comment endpoints.
    """

    @pytest.fixture
    def issue(self, user):
        """
        Create a test issue.
        """
        project = Project.objects.create(
            name='Test Project',
            description='A test project',
            created_by=user
        )
        return Issue.objects.create(
            title='Test Issue',
            description='A test issue',
            project=project,
            reporter=user
        )

    def test_create_comment(self, authenticated_client, issue):
        """
        Test creating a comment.
        """
        api_client, user = authenticated_client
        data = {
            'content': 'This is a test comment',
            'issue': issue.id,
        }
        response = api_client.post('/api/comments/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.filter(content='This is a test comment').exists()

    def test_list_comments(self, authenticated_client, issue, user):
        """
        Test listing comments.
        """
        api_client, _ = authenticated_client
        Comment.objects.create(
            content='Test comment',
            issue=issue,
            author=user
        )
        response = api_client.get('/api/comments/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_retrieve_comment(self, authenticated_client, issue, user):
        """
        Test retrieving a specific comment.
        """
        api_client, _ = authenticated_client
        comment = Comment.objects.create(
            content='Test comment',
            issue=issue,
            author=user
        )
        response = api_client.get(f'/api/comments/{comment.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Test comment'

    def test_update_comment(self, authenticated_client, issue, user):
        """
        Test updating a comment.
        """
        api_client, _ = authenticated_client
        comment = Comment.objects.create(
            content='Test comment',
            issue=issue,
            author=user
        )
        data = {'content': 'Updated comment'}
        response = api_client.patch(f'/api/comments/{comment.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        comment.refresh_from_db()
        assert comment.content == 'Updated comment'

    def test_delete_comment(self, authenticated_client, issue, user):
        """
        Test deleting a comment.
        """
        api_client, _ = authenticated_client
        comment = Comment.objects.create(
            content='Test comment',
            issue=issue,
            author=user
        )
        response = api_client.delete(f'/api/comments/{comment.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(id=comment.id).exists()

    def test_create_comment_for_issue(self, authenticated_client, issue):
        """
        Test creating a comment for a specific issue via standard endpoint.
        """
        api_client, user = authenticated_client
        data = {
            'content': 'Issue-specific comment',
            'issue': issue.id,
        }
        response = api_client.post('/api/comments/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.filter(content='Issue-specific comment', issue=issue).exists()

    def test_list_comments_by_issue(self, authenticated_client, issue, user):
        """
        Test listing comments filtered by issue.
        """
        api_client, _ = authenticated_client
        Comment.objects.create(
            content='Comment 1',
            issue=issue,
            author=user
        )
        Comment.objects.create(
            content='Comment 2',
            issue=issue,
            author=user
        )
        response = api_client.get(f'/api/comments/?issue_id={issue.id}')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_create_comment_unauthenticated(self, api_client, issue):
        """
        Test creating a comment without authentication.
        """
        data = {
            'content': 'Test comment',
            'issue': issue.id,
        }
        response = api_client.post('/api/comments/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_comment_author_set_automatically(self, authenticated_client, issue):
        """
        Test that comment author is set to current user automatically.
        """
        api_client, user = authenticated_client
        data = {
            'content': 'Test comment',
            'issue': issue.id,
        }
        response = api_client.post('/api/comments/', data)
        assert response.status_code == status.HTTP_201_CREATED
        comment = Comment.objects.get(content='Test comment')
        assert comment.author == user
