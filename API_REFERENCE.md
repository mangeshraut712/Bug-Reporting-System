# Bug Reporting System - API Reference

## Base URL
```
http://localhost:8000/api
```

## Authentication

All endpoints (except registration and login) require JWT authentication.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Storage
Tokens are stored in browser localStorage:
- `access_token`: Short-lived token (1 hour)
- `refresh_token`: Long-lived token (7 days)

---

## Authentication Endpoints

### Register User
**POST** `/auth/register/`

Create a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

**Response** (201 Created):
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Login
**POST** `/auth/login/`

Authenticate user and receive JWT tokens.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Get Current User
**GET** `/auth/users/me/`

Get information about the authenticated user.

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Logout
**POST** `/auth/logout/`

Logout the current user.

**Response** (200 OK):
```json
{
  "detail": "Successfully logged out."
}
```

---

## Projects Endpoints

### List Projects
**GET** `/projects/`

Get all projects created by the authenticated user.

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10)

**Response** (200 OK):
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "My Project",
      "description": "Project description",
      "created_by": 1,
      "created_by_name": "John Doe",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "issue_count": 5
    }
  ]
}
```

### Create Project
**POST** `/projects/`

Create a new project.

**Request Body**:
```json
{
  "name": "My Project",
  "description": "Project description"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "My Project",
  "description": "Project description",
  "created_by": 1,
  "created_by_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "issue_count": 0
}
```

### Get Project
**GET** `/projects/{id}/`

Get a specific project.

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "My Project",
  "description": "Project description",
  "created_by": 1,
  "created_by_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "issue_count": 5
}
```

### Update Project
**PATCH** `/projects/{id}/`

Update a project.

**Request Body**:
```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Updated Project Name",
  "description": "Updated description",
  "created_by": 1,
  "created_by_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "issue_count": 5
}
```

### Delete Project
**DELETE** `/projects/{id}/`

Delete a project.

**Response** (204 No Content)

### Get Project Issues
**GET** `/projects/{id}/issues/`

Get all issues for a project with optional filtering.

**Query Parameters**:
- `status`: Filter by status (open, in_progress, closed)
- `priority`: Filter by priority (low, medium, high, critical)
- `search`: Search in title and description

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Bug in login",
    "description": "Login button not working",
    "status": "open",
    "priority": "high",
    "project": 1,
    "project_name": "My Project",
    "reporter": 1,
    "reporter_name": "John Doe",
    "assignee": 2,
    "assignee_name": "Jane Smith",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "comment_count": 3
  }
]
```

---

## Issues Endpoints

### List Issues
**GET** `/issues/`

Get all issues.

**Query Parameters**:
- `project_id`: Filter by project ID
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10)

**Response** (200 OK):
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/issues/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Bug in login",
      "description": "Login button not working",
      "status": "open",
      "priority": "high",
      "project": 1,
      "project_name": "My Project",
      "reporter": 1,
      "reporter_name": "John Doe",
      "assignee": 2,
      "assignee_name": "Jane Smith",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "comment_count": 3
    }
  ]
}
```

### Create Issue
**POST** `/issues/`

Create a new issue.

**Request Body**:
```json
{
  "title": "Bug in login",
  "description": "Login button not working",
  "priority": "high",
  "project": 1,
  "assignee": 2
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "title": "Bug in login",
  "description": "Login button not working",
  "status": "open",
  "priority": "high",
  "project": 1,
  "project_name": "My Project",
  "reporter": 1,
  "reporter_name": "John Doe",
  "assignee": 2,
  "assignee_name": "Jane Smith",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "comment_count": 0
}
```

### Create Issue for Project
**POST** `/issues/create-for-project/{project_id}/`

Create an issue directly for a project.

**Request Body**:
```json
{
  "title": "Bug in login",
  "description": "Login button not working",
  "priority": "high"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "title": "Bug in login",
  "description": "Login button not working",
  "status": "open",
  "priority": "high",
  "project": 1,
  "project_name": "My Project",
  "reporter": 1,
  "reporter_name": "John Doe",
  "assignee": null,
  "assignee_name": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "comment_count": 0
}
```

### Get Issue
**GET** `/issues/{id}/`

Get a specific issue.

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Bug in login",
  "description": "Login button not working",
  "status": "open",
  "priority": "high",
  "project": 1,
  "project_name": "My Project",
  "reporter": 1,
  "reporter_name": "John Doe",
  "assignee": 2,
  "assignee_name": "Jane Smith",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "comment_count": 3
}
```

### Update Issue
**PATCH** `/issues/{id}/`

Update an issue (only reporter or assignee can update).

**Request Body**:
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "priority": "critical",
  "assignee": 3
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Updated title",
  "description": "Updated description",
  "status": "open",
  "priority": "critical",
  "project": 1,
  "project_name": "My Project",
  "reporter": 1,
  "reporter_name": "John Doe",
  "assignee": 3,
  "assignee_name": "Bob Johnson",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "comment_count": 3
}
```

### Update Issue Status
**PATCH** `/issues/{id}/update_status/`

Update only the status of an issue (only reporter or assignee can update).

**Request Body**:
```json
{
  "status": "in_progress"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Bug in login",
  "description": "Login button not working",
  "status": "in_progress",
  "priority": "high",
  "project": 1,
  "project_name": "My Project",
  "reporter": 1,
  "reporter_name": "John Doe",
  "assignee": 2,
  "assignee_name": "Jane Smith",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "comment_count": 3
}
```

### Assign Issue
**PATCH** `/issues/{id}/assign/`

Assign an issue to a user (only reporter or assignee can assign).

**Request Body**:
```json
{
  "assignee_id": 3
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Bug in login",
  "description": "Login button not working",
  "status": "open",
  "priority": "high",
  "project": 1,
  "project_name": "My Project",
  "reporter": 1,
  "reporter_name": "John Doe",
  "assignee": 3,
  "assignee_name": "Bob Johnson",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "comment_count": 3
}
```

### Delete Issue
**DELETE** `/issues/{id}/`

Delete an issue.

**Response** (204 No Content)

---

## Comments Endpoints

### List Comments
**GET** `/comments/`

Get all comments.

**Query Parameters**:
- `issue_id`: Filter by issue ID
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10)

**Response** (200 OK):
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "content": "This is a comment",
      "issue": 1,
      "author": 1,
      "author_name": "John Doe",
      "author_email": "john@example.com",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Create Comment
**POST** `/comments/`

Create a new comment.

**Request Body**:
```json
{
  "content": "This is a comment",
  "issue": 1
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "content": "This is a comment",
  "issue": 1,
  "author": 1,
  "author_name": "John Doe",
  "author_email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Create Comment for Issue
**POST** `/comments/create-for-issue/{issue_id}/`

Create a comment directly for an issue.

**Request Body**:
```json
{
  "content": "This is a comment"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "content": "This is a comment",
  "issue": 1,
  "author": 1,
  "author_name": "John Doe",
  "author_email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Get Comment
**GET** `/comments/{id}/`

Get a specific comment.

**Response** (200 OK):
```json
{
  "id": 1,
  "content": "This is a comment",
  "issue": 1,
  "author": 1,
  "author_name": "John Doe",
  "author_email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Update Comment
**PATCH** `/comments/{id}/`

Update a comment.

**Request Body**:
```json
{
  "content": "Updated comment"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "content": "Updated comment",
  "issue": 1,
  "author": 1,
  "author_name": "John Doe",
  "author_email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### Delete Comment
**DELETE** `/comments/{id}/`

Delete a comment.

**Response** (204 No Content)

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Authentication credentials were not provided or are invalid."
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "The requested resource was not found."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Status Codes

- **200 OK**: Successful GET, PATCH, or PUT request
- **201 Created**: Successful POST request
- **204 No Content**: Successful DELETE request
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## Rate Limiting

Currently, there is no rate limiting implemented. This should be added for production deployments.

---

## Pagination

List endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10)

Response includes:
- `count`: Total number of items
- `next`: URL to next page (null if last page)
- `previous`: URL to previous page (null if first page)
- `results`: Array of items

---

## Filtering

### Issues Filtering

Filter issues by status, priority, or search:
```
GET /api/projects/{id}/issues/?status=open&priority=high&search=login
```

### Comments Filtering

Filter comments by issue:
```
GET /api/comments/?issue_id=1
```

---

## Examples

### Complete Workflow

1. **Register**:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "password": "password123",
    "password_confirm": "password123"
  }'
```

2. **Login**:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

3. **Create Project**:
```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "Project description"
  }'
```

4. **Create Issue**:
```bash
curl -X POST http://localhost:8000/api/issues/create-for-project/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bug title",
    "description": "Bug description",
    "priority": "high"
  }'
```

5. **Add Comment**:
```bash
curl -X POST http://localhost:8000/api/comments/create-for-issue/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a comment"
  }'
```
