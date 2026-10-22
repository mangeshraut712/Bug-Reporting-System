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

    def test_create_for_project_sets_reporter(self, authenticated_client, project, another_user):
        """
        The project shortcut creates an open issue reported by the caller.
        """
        api_client, user = authenticated_client
        response = api_client.post(
            f'/api/issues/create-for-project/{project.id}/',
            {
                'title': 'Shortcut issue',
                'description': 'Created from the project page',
                'priority': 'low',
                'reporter': another_user.id,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        issue = Issue.objects.get(title='Shortcut issue')
        assert issue.reporter == user
        assert issue.project == project
        assert issue.status == 'open'
        assert response.data['project_name'] == project.name
        assert response.data['comment_count'] == 0

    def test_create_for_project_rejects_blank_title(self, authenticated_client, project):
        """
        The project shortcut still validates the issue payload.
        """
        api_client, _ = authenticated_client
        response = api_client.post(
            f'/api/issues/create-for-project/{project.id}/',
            {'title': '', 'description': 'Missing title'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Issue.objects.filter(description='Missing title').exists()

    def test_create_for_missing_project(self, authenticated_client):
        """
        Creating an issue for a missing project returns 404.
        """
        api_client, _ = authenticated_client
        response = api_client.post(
            '/api/issues/create-for-project/99999/',
            {'title': 'Missing', 'description': 'No project'},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['error'] == 'Not Found'

    def test_update_status_requires_status(self, authenticated_client, project, user):
        """
        A status update without a status is rejected.
        """
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Needs a status',
            description='Missing field',
            project=project,
            reporter=user,
        )
        response = api_client.patch(f'/api/issues/{issue.id}/update_status/', {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        issue.refresh_from_db()
        assert issue.status == 'open'

    def test_assign_unknown_user(self, authenticated_client, project, user):
        """
        Assigning an issue to a missing user returns 404.
        """
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Unassigned',
            description='Nobody home',
            project=project,
            reporter=user,
        )
        response = api_client.patch(f'/api/issues/{issue.id}/assign/', {'assignee_id': 99999})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['error'] == 'User not found.'

    def test_assign_clears_assignee_when_omitted(self, authenticated_client, project, user):
        """
        An assign call without an assignee clears the current assignee.
        """
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Assigned',
            description='Will be cleared',
            project=project,
            reporter=user,
            assignee=user,
        )
        response = api_client.patch(f'/api/issues/{issue.id}/assign/', {})
        assert response.status_code == status.HTTP_200_OK
        issue.refresh_from_db()
        assert issue.assignee is None

    def test_stranger_cannot_update_issue(self, authenticated_client_other, project, user):
        """
        Someone who is neither reporter nor assignee cannot edit the issue.
        """
        api_client, _ = authenticated_client_other
        issue = Issue.objects.create(
            title='Protected',
            description='Only the reporter can edit this',
            project=project,
            reporter=user,
        )
        response = api_client.patch(f'/api/issues/{issue.id}/', {'title': 'Hijacked'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['error'] == 'Forbidden'
        issue.refresh_from_db()
        assert issue.title == 'Protected'

    def test_assignee_can_update_issue(self, authenticated_client_other, project, user, another_user):
        """
        The assignee can change the issue.
        """
        api_client, _ = authenticated_client_other
        issue = Issue.objects.create(
            title='Assigned work',
            description='The assignee should be able to edit this',
            project=project,
            reporter=user,
            assignee=another_user,
        )
        response = api_client.patch(f'/api/issues/{issue.id}/', {'title': 'Updated by assignee'})
        assert response.status_code == status.HTTP_200_OK
        issue.refresh_from_db()
        assert issue.title == 'Updated by assignee'

    def test_invalid_status_rejected_on_update(self, authenticated_client, project, user):
        """
        Issue updates only accept the known status values.
        """
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Status check',
            description='Invalid status should fail',
            project=project,
            reporter=user,
        )
        response = api_client.patch(f'/api/issues/{issue.id}/', {'status': 'not-a-status'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        issue.refresh_from_db()
        assert issue.status == 'open'

    def test_list_issues_filtered_by_project(self, authenticated_client, project, user):
        """
        Issue lists can be limited to one project and are paginated.
        """
        api_client, _ = authenticated_client
        for index in range(11):
            Issue.objects.create(
                title=f'Issue {index}',
                description='Pagination filler',
                project=project,
                reporter=user,
            )
        response = api_client.get(f'/api/issues/?project_id={project.id}')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 11
        assert len(response.data['results']) == 10
        assert response.data['next']

    def test_issue_string_and_clean(self, issue):
        """
        An issue displays its title and accepts a valid assignee.
        """
        assert str(issue) == 'Test Issue'
        issue.clean()
