"""
Tests for issues app.
"""
import pytest
from rest_framework import status
from projects.models import Project
from .models import Issue


@pytest.mark.django_db
class TestIssueEndpoints:
    """
    Test issue endpoints.
    """

    @pytest.fixture
    def project(self, user):
        """
        Create a test project.
        """
        return Project.objects.create(
            name='Test Project',
            description='A test project',
            created_by=user
        )

    def test_create_issue(self, authenticated_client, project):
        """
        Test creating an issue.
        """
        api_client, user = authenticated_client
        data = {
            'title': 'Test Issue',
            'description': 'A test issue',
            'priority': 'high',
            'project': project.id,
        }
        response = api_client.post('/api/issues/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Issue.objects.filter(title='Test Issue').exists()

    def test_list_issues(self, authenticated_client, project, user):
        """
        Test listing issues.
        """
        api_client, _ = authenticated_client
        Issue.objects.create(
            title='Test Issue',
            description='A test issue',
            project=project,
            reporter=user
        )
        response = api_client.get('/api/issues/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_retrieve_issue(self, authenticated_client, project, user):
        """
        Test retrieving a specific issue.
        """
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Test Issue',
            description='A test issue',
            project=project,
            reporter=user
        )
        response = api_client.get(f'/api/issues/{issue.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Issue'

    def test_update_issue_status(self, authenticated_client, project, user):
        """
        Test updating issue status.
        """
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Test Issue',
            description='A test issue',
            project=project,
            reporter=user,
            status='open'
        )
        data = {'status': 'in_progress'}
        response = api_client.patch(f'/api/issues/{issue.id}/update_status/', data)
        assert response.status_code == status.HTTP_200_OK
        issue.refresh_from_db()
        assert issue.status == 'in_progress'

    def test_assign_issue(self, authenticated_client, project, user):
        """
        Test assigning an issue.
        """
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Test Issue',
            description='A test issue',
            project=project,
            reporter=user
        )
        data = {'assignee_id': user.id}
        response = api_client.patch(f'/api/issues/{issue.id}/assign/', data)
        assert response.status_code == status.HTTP_200_OK
        issue.refresh_from_db()
        assert issue.assignee == user

    def test_delete_issue(self, authenticated_client, project, user):
        """
        Test deleting an issue.
        """
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Test Issue',
            description='A test issue',
            project=project,
            reporter=user
        )
        response = api_client.delete(f'/api/issues/{issue.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Issue.objects.filter(id=issue.id).exists()

    def test_create_issue_for_project(self, authenticated_client, project):
        """
        Test creating an issue for a specific project via standard endpoint.
        """
        api_client, user = authenticated_client
        data = {
            'title': 'Project Issue',
            'description': 'An issue for the project',
            'priority': 'critical',
            'project': project.id,
        }
        response = api_client.post('/api/issues/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Issue.objects.filter(title='Project Issue', project=project).exists()

    def test_update_issue_status_by_reporter(self, authenticated_client, project, user):
        """
        Test that reporter can update issue status.
        """
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Test Issue',
            description='A test issue',
            project=project,
            reporter=user,
            status='open'
        )
        data = {'status': 'in_progress'}
        response = api_client.patch(f'/api/issues/{issue.id}/update_status/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'in_progress'

    def test_issue_status_choices(self, authenticated_client, project, user):
        """
        Test that valid status choices are accepted.
        """
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Test Issue',
            description='A test issue',
            project=project,
            reporter=user
        )
        data = {'status': 'closed'}
        response = api_client.patch(f'/api/issues/{issue.id}/update_status/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'closed'

    def test_issue_priority_choices(self, authenticated_client, project):
        """
        Test that only valid priority choices are accepted.
        """
        api_client, user = authenticated_client
        data = {
            'title': 'Test Issue',
            'description': 'A test issue',
            'priority': 'invalid_priority',
            'project': project.id,
        }
        response = api_client.post('/api/issues/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_issue_unauthenticated(self, api_client, project):
        """
        Test creating an issue without authentication.
        """
        data = {
            'title': 'Test Issue',
            'description': 'A test issue',
            'project': project.id,
        }
        response = api_client.post('/api/issues/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
