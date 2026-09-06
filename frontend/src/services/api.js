import axios from 'axios';
import {
  demoAuthAPI,
  demoCommentsAPI,
  demoIssuesAPI,
  demoProjectsAPI,
  isDemoMode,
} from './demoStore';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh and errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !isDemoMode()) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      const base = (process.env.PUBLIC_URL || '').replace(/\/$/, '');
      window.location.href = `${base}/login`;
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  register: (data) => (isDemoMode() ? demoAuthAPI.register(data) : api.post('/auth/register/', data)),
  login: (email, password) =>
    isDemoMode() ? demoAuthAPI.login(email, password) : api.post('/auth/login/', { email, password }),
  logout: () => (isDemoMode() ? demoAuthAPI.logout() : api.post('/auth/logout/')),
  getCurrentUser: () => (isDemoMode() ? demoAuthAPI.getCurrentUser() : api.get('/auth/users/me/')),
};

// Projects API calls
export const projectsAPI = {
  list: () => (isDemoMode() ? demoProjectsAPI.list() : api.get('/projects/')),
  create: (data) => (isDemoMode() ? demoProjectsAPI.create(data) : api.post('/projects/', data)),
  retrieve: (id) => (isDemoMode() ? demoProjectsAPI.retrieve(id) : api.get(`/projects/${id}/`)),
  update: (id, data) =>
    isDemoMode() ? demoProjectsAPI.update(id, data) : api.patch(`/projects/${id}/`, data),
  delete: (id) => (isDemoMode() ? demoProjectsAPI.delete(id) : api.delete(`/projects/${id}/`)),
  getIssues: (id, params = {}) =>
    isDemoMode()
      ? demoProjectsAPI.getIssues(id, params)
      : api.get(`/projects/${id}/issues/`, { params }),
};

// Issues API calls
export const issuesAPI = {
  list: (params = {}) => (isDemoMode() ? demoIssuesAPI.list(params) : api.get('/issues/', { params })),
  create: (data) => (isDemoMode() ? demoIssuesAPI.create(data) : api.post('/issues/', data)),
  retrieve: (id) => (isDemoMode() ? demoIssuesAPI.retrieve(id) : api.get(`/issues/${id}/`)),
  update: (id, data) =>
    isDemoMode() ? demoIssuesAPI.update(id, data) : api.patch(`/issues/${id}/`, data),
  delete: (id) => (isDemoMode() ? demoIssuesAPI.delete(id) : api.delete(`/issues/${id}/`)),
  createForProject: (projectId, data) =>
    isDemoMode()
      ? demoIssuesAPI.createForProject(projectId, data)
      : api.post(`/issues/create-for-project/${projectId}/`, data),
  updateStatus: (id, status) =>
    isDemoMode()
      ? demoIssuesAPI.updateStatus(id, status)
      : api.patch(`/issues/${id}/update_status/`, { status }),
  assign: (id, assigneeId) =>
    isDemoMode()
      ? demoIssuesAPI.assign(id, assigneeId)
      : api.patch(`/issues/${id}/assign/`, { assignee_id: assigneeId }),
};

// Comments API calls
export const commentsAPI = {
  list: (params = {}) =>
    isDemoMode() ? demoCommentsAPI.list(params) : api.get('/comments/', { params }),
  create: (data) => (isDemoMode() ? demoCommentsAPI.create(data) : api.post('/comments/', data)),
  retrieve: (id) => (isDemoMode() ? demoCommentsAPI.retrieve(id) : api.get(`/comments/${id}/`)),
  update: (id, data) =>
    isDemoMode() ? demoCommentsAPI.update(id, data) : api.patch(`/comments/${id}/`, data),
  delete: (id) => (isDemoMode() ? demoCommentsAPI.delete(id) : api.delete(`/comments/${id}/`)),
  createForIssue: (issueId, data) =>
    isDemoMode()
      ? demoCommentsAPI.createForIssue(issueId, data)
      : api.post(`/comments/create-for-issue/${issueId}/`, data),
};

export default api;
