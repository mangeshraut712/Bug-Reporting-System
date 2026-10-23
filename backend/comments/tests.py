"""
Tests for comments app.
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from issues.models import Issue
from projects.models import Project

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
        assert response.data['count'] >= 1
        assert any(item['content'] == 'Test comment' for item in response.data['results'])

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

    def test_create_for_issue_sets_author(self, authenticated_client, issue, another_user):
        """
        The issue shortcut stores the comment on that issue as the caller.
        """
        api_client, user = authenticated_client
        response = api_client.post(
            f'/api/comments/create-for-issue/{issue.id}/',
            {'content': 'Shortcut comment', 'author': another_user.id},
        )
        assert response.status_code == status.HTTP_201_CREATED
        comment = Comment.objects.get(content='Shortcut comment')
        assert comment.author == user
        assert comment.issue == issue
        assert response.data['author_email'] == user.email
        assert response.data['author_name'] == user.get_full_name()

    def test_create_for_issue_rejects_blank_content(self, authenticated_client, issue):
        """
        The issue shortcut still requires comment content.
        """
        api_client, _ = authenticated_client
        response = api_client.post(f'/api/comments/create-for-issue/{issue.id}/', {'content': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert issue.comments.count() == 0

    def test_create_for_missing_issue(self, authenticated_client):
        """
        Commenting on a missing issue returns 404.
        """
        api_client, _ = authenticated_client
        response = api_client.post(
            '/api/comments/create-for-issue/99999/',
            {'content': 'Nowhere'},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['error'] == 'Not Found'

    def test_empty_comment_rejected(self, authenticated_client, issue):
        """
        A comment needs content.
        """
        api_client, _ = authenticated_client
        response = api_client.post('/api/comments/', {'content': '', 'issue': issue.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Comment.objects.filter(issue=issue, content='').exists()

    def test_comment_string(self, comment):
        """
        A comment names its author and issue.
        """
        assert str(comment.issue) in str(comment)
        assert 'Comment by' in str(comment)

    def test_stranger_cannot_edit_or_delete_comment(
        self, authenticated_client_other, issue, user
    ):
        """
        Only the author can change a comment.
        """
        api_client, _other = authenticated_client_other
        comment = Comment.objects.create(content='Original', issue=issue, author=user)
        update = api_client.patch(f'/api/comments/{comment.id}/', {'content': 'Hijacked'})
        remove = api_client.delete(f'/api/comments/{comment.id}/')
        assert update.status_code == status.HTTP_403_FORBIDDEN
        assert update.data['error'] == 'Forbidden'
        assert remove.status_code == status.HTTP_403_FORBIDDEN
        comment.refresh_from_db()
        assert comment.content == 'Original'

    def test_whitespace_comment_rejected(self, authenticated_client, issue):
        """
        A comment that is only whitespace is rejected.
        """
        api_client, _user = authenticated_client
        response = api_client.post('/api/comments/', {'content': '   ', 'issue': issue.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert issue.comments.count() == 0

    def test_oversized_comment_rejected(self, authenticated_client, issue):
        """
        Comment text has an upper bound.
        """
        api_client, _user = authenticated_client
        response = api_client.post('/api/comments/', {
            'content': 'a' * 5001,
            'issue': issue.id,
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert issue.comments.count() == 0

    def test_invalid_issue_filter_is_400(self, authenticated_client):
        """
        A non-numeric issue filter does not raise a server error.
        """
        api_client, _user = authenticated_client
        response = api_client.get('/api/comments/?issue_id=nope')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_for_issue_rejects_non_numeric_id(self, authenticated_client):
        """
        The issue shortcut rejects a non-numeric issue id.
        """
        api_client, _user = authenticated_client
        response = api_client.post(
            '/api/comments/create-for-issue/abc/',
            {'content': 'Nowhere'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Comment.objects.filter(content='Nowhere').exists()

    def test_invalid_comment_lookup_is_400(self, authenticated_client):
        """
        A non-numeric comment id is a client error.
        """
        api_client, _user = authenticated_client
        response = api_client.get('/api/comments/abc/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_deleted_author_serializes(self, authenticated_client, issue, user, another_user):
        """
        A comment remains readable after its author is deleted.
        """
        comment = Comment.objects.create(content='Still here', issue=issue, author=user)
        user.delete()
        comment.refresh_from_db()
        client = APIClient()
        refresh = RefreshToken.for_user(another_user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = client.get(f'/api/comments/{comment.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['author'] is None
        assert response.data['author_name'] is None
        assert response.data['author_email'] is None
        assert response.data['content'] == 'Still here'
        assert 'deleted user' in str(comment)
