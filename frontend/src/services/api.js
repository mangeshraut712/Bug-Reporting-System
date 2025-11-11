import axios from 'axios';

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
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (email, password) => api.post('/auth/login/', { email, password }),
  logout: () => api.post('/auth/logout/'),
  getCurrentUser: () => api.get('/auth/users/me/'),
};

// Projects API calls
export const projectsAPI = {
  list: () => api.get('/projects/'),
  create: (data) => api.post('/projects/', data),
  retrieve: (id) => api.get(`/projects/${id}/`),
  update: (id, data) => api.patch(`/projects/${id}/`, data),
  delete: (id) => api.delete(`/projects/${id}/`),
  getIssues: (id, params = {}) => api.get(`/projects/${id}/issues/`, { params }),
};

// Issues API calls
export const issuesAPI = {
  list: (params = {}) => api.get('/issues/', { params }),
  create: (data) => api.post('/issues/', data),
  retrieve: (id) => api.get(`/issues/${id}/`),
  update: (id, data) => api.patch(`/issues/${id}/`, data),
  delete: (id) => api.delete(`/issues/${id}/`),
  createForProject: (projectId, data) => 
    api.post(`/issues/create-for-project/${projectId}/`, data),
  updateStatus: (id, status) => 
    api.patch(`/issues/${id}/update_status/`, { status }),
  assign: (id, assigneeId) => 
    api.patch(`/issues/${id}/assign/`, { assignee_id: assigneeId }),
};

// Comments API calls
export const commentsAPI = {
  list: (params = {}) => api.get('/comments/', { params }),
  create: (data) => api.post('/comments/', data),
  retrieve: (id) => api.get(`/comments/${id}/`),
  update: (id, data) => api.patch(`/comments/${id}/`, data),
  delete: (id) => api.delete(`/comments/${id}/`),
  createForIssue: (issueId, data) => 
    api.post(`/comments/create-for-issue/${issueId}/`, data),
};

export default api;
