"""
Tests for IssueViewSet's custom actions (assign, update_status, create-for-project).

These actions are gated through MUTATING_ACTIONS in get_permissions(), parse
ids via parse_positive_int, and force reporter/project server-side. A refactor
that drops any of those (e.g. a new mutating action missing from
MUTATING_ACTIONS) silently opens a write path, so the contract is pinned here.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from issues.models import Issue
from projects.models import Project

User = get_user_model()

pytestmark = pytest.mark.django_db


def make_user(username):
    return User.objects.create_user(
        email=f'{username}@example.com',
        username=username,
        password='testpass123',
    )


def make_project(owner, name='Project'):
    return Project.objects.create(name=name, description='A project', created_by=owner)


def make_issue(owner, project=None, **overrides):
    if project is None:
        project = make_project(owner)
    return Issue.objects.create(
        project=project,
        reporter=owner,
        title='Broken button',
        description='Clicking the button does nothing',
        **overrides,
    )


class TestAssignAction:
    def test_non_reporter_or_assignee_cannot_assign(self, api_client):
        owner = make_user('assignowner')
        stranger = make_user('assignstranger')
        issue = make_issue(owner)
        api_client.force_authenticate(user=stranger)
        response = api_client.patch(
            f'/api/issues/{issue.id}/assign/',
            {'assignee_id': stranger.id},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        issue.refresh_from_db()
        assert issue.assignee is None

    def test_inactive_user_cannot_be_assigned(self, api_client):
        owner = make_user('activeowner')
        inactive = make_user('inactiveuser')
        inactive.is_active = False
        inactive.save()
        issue = make_issue(owner)
        api_client.force_authenticate(user=owner)
        response = api_client.patch(
            f'/api/issues/{issue.id}/assign/',
            {'assignee_id': inactive.id},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        issue.refresh_from_db()
        assert issue.assignee is None

    def test_blank_assignee_id_unassigns(self, api_client):
        owner = make_user('unassignowner')
        other = make_user('currentassignee')
        issue = make_issue(owner, assignee=other)
        api_client.force_authenticate(user=owner)
        response = api_client.patch(
            f'/api/issues/{issue.id}/assign/',
            {'assignee_id': ''},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        issue.refresh_from_db()
        assert issue.assignee is None

    def test_non_object_body_rejected(self, api_client):
        owner = make_user('bodyowner')
        issue = make_issue(owner)
        api_client.force_authenticate(user=owner)
        response = api_client.patch(
            f'/api/issues/{issue.id}/assign/',
            ['assignee_id'],
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        issue.refresh_from_db()
        assert issue.assignee_id is None


class TestUpdateStatusAction:
    def test_blank_status_rejected(self, api_client):
        owner = make_user('statusowner')
        issue = make_issue(owner)
        previous = issue.status
        api_client.force_authenticate(user=owner)
        response = api_client.patch(
            f'/api/issues/{issue.id}/update_status/',
            {'status': ''},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        issue.refresh_from_db()
        assert issue.status == previous

    def test_invalid_status_rejected(self, api_client):
        owner = make_user('statusowner2')
        issue = make_issue(owner)
        previous = issue.status
        api_client.force_authenticate(user=owner)
        response = api_client.patch(
            f'/api/issues/{issue.id}/update_status/',
            {'status': 'not-a-valid-status'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        issue.refresh_from_db()
        assert issue.status == previous

    def test_non_reporter_or_assignee_cannot_change_status(self, api_client):
        owner = make_user('statusowner3')
        stranger = make_user('statusstranger')
        issue = make_issue(owner)
        previous = issue.status
        api_client.force_authenticate(user=stranger)
        response = api_client.patch(
            f'/api/issues/{issue.id}/update_status/',
            {'status': 'closed'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        issue.refresh_from_db()
        assert issue.status == previous


class TestCreateForProjectAction:
    def test_reporter_and_project_taken_from_url_and_user(self, api_client):
        requester = make_user('issuereporter')
        other = make_user('impostor')
        project = make_project(requester, name='Target')
        other_project = make_project(requester, name='Decoy')
        api_client.force_authenticate(user=requester)
        response = api_client.post(
            f'/api/issues/create-for-project/{project.id}/',
            {
                'title': 'New bug',
                'description': 'It crashes',
                'reporter': other.id,
                'project': other_project.id,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        issue = Issue.objects.get(pk=response.data['id'])
        assert issue.reporter_id == requester.id
        assert issue.project_id == project.id

    def test_requires_authentication(self, api_client):
        owner = make_user('anonprojectowner')
        project = make_project(owner)
        response = api_client.post(
            f'/api/issues/create-for-project/{project.id}/',
            {'title': 'New bug', 'description': 'It crashes'},
            format='json',
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Issue.objects.count() == 0
