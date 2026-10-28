"""
Tests for issues app.
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from comments.models import Comment
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
        assert response.data['count'] >= 1
        assert any(item['title'] == 'Test Issue' for item in response.data['results'])

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

    def test_create_for_project_rejects_list_payload_without_creating_an_issue(
        self, authenticated_client, project
    ):
        """A shortcut create needs a JSON object, not an array payload."""
        api_client, _ = authenticated_client
        issue_count = Issue.objects.count()

        response = api_client.post(
            f'/api/issues/create-for-project/{project.id}/',
            [],
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Issue.objects.count() == issue_count

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

    def test_update_status_rejects_list_payload_without_changing_the_issue(
        self, authenticated_client, project, user
    ):
        """A malformed status payload cannot change an issue."""
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Needs a valid payload',
            description='Array bodies are not status updates',
            project=project,
            reporter=user,
        )

        response = api_client.patch(
            f'/api/issues/{issue.id}/update_status/',
            [],
            format='json',
        )

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

    def test_assign_rejects_list_payload_without_clearing_the_assignee(
        self, authenticated_client, project, user
    ):
        """A malformed assignment payload cannot unassign an existing owner."""
        api_client, _ = authenticated_client
        issue = Issue.objects.create(
            title='Keep assignee',
            description='An array is not an unassign request',
            project=project,
            reporter=user,
            assignee=user,
        )

        response = api_client.patch(
            f'/api/issues/{issue.id}/assign/',
            [],
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        issue.refresh_from_db()
        assert issue.assignee == user

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

    def test_clean_rejects_unknown_status(self, issue):
        """
        Model validation rejects a status outside the supported choices.
        """
        issue.status = 'bogus'
        with pytest.raises(ValidationError):
            issue.clean()

    def test_database_rejects_invalid_status(self, issue):
        """
        The database constraint rejects a status the serializer did not see.
        """
        issue.status = 'bogus'
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                issue.save()
        issue.refresh_from_db()
        assert issue.status == 'open'

    def test_stranger_cannot_update_status_or_assign(self, authenticated_client_other, project, user):
        """
        Someone who is neither reporter nor assignee cannot change status or assignee.
        """
        api_client, _other = authenticated_client_other
        issue = Issue.objects.create(
            title='Protected status',
            description='Leave this alone',
            project=project,
            reporter=user,
            status='open',
        )
        status_response = api_client.patch(
            f'/api/issues/{issue.id}/update_status/',
            {'status': 'closed'},
        )
        assign_response = api_client.patch(
            f'/api/issues/{issue.id}/assign/',
            {'assignee_id': user.id},
        )
        delete_response = api_client.delete(f'/api/issues/{issue.id}/')
        assert status_response.status_code == status.HTTP_403_FORBIDDEN
        assert assign_response.status_code == status.HTTP_403_FORBIDDEN
        assert delete_response.status_code == status.HTTP_403_FORBIDDEN
        issue.refresh_from_db()
        assert issue.status == 'open'
        assert issue.assignee_id is None

    def test_update_status_rejects_unknown_value(self, authenticated_client, project, user):
        """
        The status action uses the same choices as the serializer.
        """
        api_client, _user = authenticated_client
        issue = Issue.objects.create(
            title='Status check',
            description='Invalid status should fail',
            project=project,
            reporter=user,
        )
        response = api_client.patch(
            f'/api/issues/{issue.id}/update_status/',
            {'status': 'hacked'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        issue.refresh_from_db()
        assert issue.status == 'open'

    def test_assign_rejects_non_integer_id(self, authenticated_client, project, user):
        """
        A malformed assignee id is a client error.
        """
        api_client, _user = authenticated_client
        issue = Issue.objects.create(
            title='Bad assignee',
            description='Not a number',
            project=project,
            reporter=user,
        )
        response = api_client.patch(
            f'/api/issues/{issue.id}/assign/',
            {'assignee_id': 'not-an-id'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        issue.refresh_from_db()
        assert issue.assignee_id is None

    def test_invalid_project_filter_is_400(self, authenticated_client):
        """
        A non-numeric project filter does not raise a server error.
        """
        api_client, _user = authenticated_client
        for project_id in ('abc', '0', '-1'):
            response = api_client.get(f'/api/issues/?project_id={project_id}')
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_out_of_range_project_filter_is_400(self, authenticated_client):
        """An integer beyond the database key range is a client error, not a 500."""
        api_client, _user = authenticated_client

        response = api_client.get('/api/issues/?project_id=9223372036854775808')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_issue_lookup_is_400(self, authenticated_client):
        """
        A non-numeric issue id is a client error.
        """
        api_client, _user = authenticated_client
        response = api_client.get('/api/issues/abc/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_for_project_rejects_non_numeric_id(self, authenticated_client):
        """
        The project shortcut rejects a non-numeric project id.
        """
        api_client, _user = authenticated_client
        response = api_client.post(
            '/api/issues/create-for-project/abc/',
            {'title': 'Missing', 'description': 'No project'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Issue.objects.filter(title='Missing').exists()

    def test_whitespace_title_rejected(self, authenticated_client, project):
        """
        A title that is only whitespace is rejected.
        """
        api_client, _user = authenticated_client
        response = api_client.post('/api/issues/', {
            'title': '   ',
            'description': 'Has a description',
            'project': project.id,
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Issue.objects.filter(description='Has a description').exists()

    def test_deleted_reporter_serializes(self, authenticated_client, project, user):
        """
        An issue remains readable after its reporter is removed.
        """
        issue = Issue.objects.create(
            title='Orphaned',
            description='Reporter went away',
            project=project,
            reporter=user,
        )
        user.delete()
        other = get_user_model().objects.create_user(
            email='reader@example.com',
            username='issuereader',
            password='testpass123',
        )
        client = APIClient()
        refresh = RefreshToken.for_user(other)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = client.get(f'/api/issues/{issue.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['reporter'] is None
        assert response.data['reporter_name'] is None
        assert response.data['project_created_by'] is None
        assert response.data['title'] == 'Orphaned'

    def test_list_issues_filters_status_priority_and_search(self, authenticated_client, project, user):
        """The issue list honors the same filters as a project's issue list."""
        api_client, _user = authenticated_client
        Issue.objects.create(
            title='Checkout crash',
            description='Guests cannot pay',
            status='open',
            priority='high',
            project=project,
            reporter=user,
        )
        Issue.objects.create(
            title='Receipt email',
            description='The tax row is missing',
            status='closed',
            priority='low',
            project=project,
            reporter=user,
        )
        response = api_client.get('/api/issues/?status=closed&priority=low&search=tax')
        assert response.status_code == status.HTTP_200_OK
        assert [item['title'] for item in response.data['results']] == ['Receipt email']

    def test_list_issues_rejects_unknown_status_filter(self, authenticated_client):
        """An unknown status filter is a client error on the issue list too."""
        api_client, _user = authenticated_client
        response = api_client.get('/api/issues/?status=hacked')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_project_owner_can_remove_an_issue_they_did_not_report(
        self, authenticated_client, project, another_user
    ):
        """The project creator can moderate issues filed by someone else."""
        api_client, _owner = authenticated_client
        issue = Issue.objects.create(
            title='Filed by someone else',
            description='The owner should still be able to remove it',
            project=project,
            reporter=another_user,
        )
        response = api_client.delete(f'/api/issues/{issue.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Issue.objects.filter(id=issue.id).exists()

    def test_issue_cannot_be_moved_to_another_project(self, authenticated_client, project, user):
        """Updating an issue does not change the project it belongs to."""
        api_client, _user = authenticated_client
        issue = Issue.objects.create(
            title='Stay put',
            description='Do not move this',
            project=project,
            reporter=user,
        )
        other = Project.objects.create(
            name='Elsewhere',
            description='A different project',
            created_by=user,
        )
        response = api_client.patch(f'/api/issues/{issue.id}/', {
            'project': other.id,
            'title': 'Renamed',
        })
        assert response.status_code == status.HTTP_200_OK
        issue.refresh_from_db()
        assert issue.project_id == project.id
        assert issue.title == 'Renamed'

    def test_inactive_user_cannot_be_assigned(
        self, authenticated_client, project, user, another_user
    ):
        """Disabled accounts are not valid assignees."""
        api_client, _user = authenticated_client
        another_user.is_active = False
        another_user.save(update_fields=['is_active'])
        issue = Issue.objects.create(
            title='Unassigned',
            description='Leave this with nobody inactive',
            project=project,
            reporter=user,
        )
        via_action = api_client.patch(
            f'/api/issues/{issue.id}/assign/',
            {'assignee_id': another_user.id},
        )
        via_update = api_client.patch(
            f'/api/issues/{issue.id}/',
            {'assignee': another_user.id},
        )
        assert via_action.status_code == status.HTTP_400_BAD_REQUEST
        assert via_update.status_code == status.HTTP_400_BAD_REQUEST
        issue.refresh_from_db()
        assert issue.assignee_id is None

    def test_oversized_description_rejected(self, authenticated_client, project):
        """Issue descriptions have an upper bound."""
        api_client, _user = authenticated_client
        response = api_client.post('/api/issues/', {
            'title': 'Too long',
            'description': 'd' * 10_001,
            'project': project.id,
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Issue.objects.filter(title='Too long').exists()

    def test_issue_list_counts_comments_without_a_query_per_issue(
        self, authenticated_client, project, user
    ):
        """Listing issues counts comments in the list query."""
        api_client, _user = authenticated_client
        for index in range(6):
            issue = Issue.objects.create(
                title=f'Thread {index}',
                description='Has one comment',
                project=project,
                reporter=user,
            )
            Comment.objects.create(content=f'Note {index}', issue=issue, author=user)
        with CaptureQueriesContext(connection) as captured:
            response = api_client.get(f'/api/issues/?project_id={project.id}')
        assert response.status_code == status.HTTP_200_OK
        assert [item['title'] for item in response.data['results']] == [
            'Thread 5', 'Thread 4', 'Thread 3', 'Thread 2', 'Thread 1', 'Thread 0',
        ]
        assert [item['comment_count'] for item in response.data['results']] == [1, 1, 1, 1, 1, 1]
        assert len(captured) <= 5
