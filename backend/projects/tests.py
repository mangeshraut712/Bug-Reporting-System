"""
Tests for projects app.
"""
import pytest
from rest_framework import status
from .models import Project


@pytest.mark.django_db
class TestProjectEndpoints:
    """
    Test project endpoints.
    """

    def test_create_project(self, authenticated_client):
        """
        Test creating a project.
        """
        api_client, user = authenticated_client
        data = {
            'name': 'Test Project',
            'description': 'A test project',
        }
        response = api_client.post('/api/projects/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Project.objects.filter(name='Test Project').exists()

    def test_list_projects(self, authenticated_client):
        """
        Test listing projects.
        """
        api_client, user = authenticated_client
        Project.objects.create(
            name='Test Project',
            description='A test project',
            created_by=user
        )
        response = api_client.get('/api/projects/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_retrieve_project(self, authenticated_client):
        """
        Test retrieving a specific project.
        """
        api_client, user = authenticated_client
        project = Project.objects.create(
            name='Test Project',
            description='A test project',
            created_by=user
        )
        response = api_client.get(f'/api/projects/{project.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Project'

    def test_update_project(self, authenticated_client):
        """
        Test updating a project.
        """
        api_client, user = authenticated_client
        project = Project.objects.create(
            name='Test Project',
            description='A test project',
            created_by=user
        )
        data = {'name': 'Updated Project'}
        response = api_client.patch(f'/api/projects/{project.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        project.refresh_from_db()
        assert project.name == 'Updated Project'

    def test_delete_project(self, authenticated_client):
        """
        Test deleting a project.
        """
        api_client, user = authenticated_client
        project = Project.objects.create(
            name='Test Project',
            description='A test project',
            created_by=user
        )
        response = api_client.delete(f'/api/projects/{project.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(id=project.id).exists()

    def test_get_project_issues(self, authenticated_client, project):
        """
        Test getting issues for a project.
        """
        api_client, user = authenticated_client
        from issues.models import Issue
        Issue.objects.create(
            title='Issue 1',
            description='First issue',
            status='open',
            priority='high',
            project=project,
            reporter=user
        )
        Issue.objects.create(
            title='Issue 2',
            description='Second issue',
            status='closed',
            priority='low',
            project=project,
            reporter=user
        )
        response = api_client.get(f'/api/projects/{project.id}/issues/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_get_project_issues_filtered_by_status(self, authenticated_client, project):
        """
        Test filtering project issues by status.
        """
        api_client, user = authenticated_client
        from issues.models import Issue
        Issue.objects.create(
            title='Open Issue',
            description='An open issue',
            status='open',
            priority='high',
            project=project,
            reporter=user
        )
        Issue.objects.create(
            title='Closed Issue',
            description='A closed issue',
            status='closed',
            priority='low',
            project=project,
            reporter=user
        )
        response = api_client.get(f'/api/projects/{project.id}/issues/?status=open')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['status'] == 'open'

    def test_create_project_unauthenticated(self, api_client):
        """
        Test creating a project without authentication.
        """
        data = {
            'name': 'Test Project',
            'description': 'A test project',
        }
        response = api_client.post('/api/projects/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
