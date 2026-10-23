import axios from 'axios';
import {
  demoAuthAPI,
  demoCommentsAPI,
  demoIssuesAPI,
  demoProjectsAPI,
  isDemoMode,
} from './demoStore';

const API_BASE_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const REFRESH_PATH = '/auth/token/refresh/';
const UNAUTHENTICATED_PATHS = [
  '/auth/login/',
  '/auth/register/',
  '/auth/logout/',
  REFRESH_PATH,
];

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

function isUnauthenticatedPath(url) {
  return UNAUTHENTICATED_PATHS.some((path) => (url || '').includes(path));
}

function apiBase() {
  const origin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost';
  return new URL(API_BASE_URL, origin);
}

function safeNextPath(nextUrl) {
  if (!nextUrl || typeof nextUrl !== 'string') {
    return null;
  }
  try {
    const base = apiBase();
    const next = new URL(nextUrl, base);
    if (next.origin !== base.origin) {
      return null;
    }
    const basePath = base.pathname.replace(/\/$/, '');
    if (next.pathname !== basePath && !next.pathname.startsWith(`${basePath}/`)) {
      return null;
    }
    return `${next.pathname}${next.search}`;
  } catch {
    return null;
  }
}

export function asList(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }
  if (payload && Array.isArray(payload.results)) {
    return payload.results;
  }
  return [];
}

async function getAllPages(path, params) {
  const collected = [];
  let nextPath = path;
  let nextParams = params;
  const seen = new Set();
  for (let page = 0; page < 20 && nextPath; page += 1) {
    if (seen.has(nextPath)) {
      break;
    }
    seen.add(nextPath);
    const response = await api.get(nextPath, nextParams ? { params: nextParams } : undefined);
    const payload = response.data;
    if (Array.isArray(payload)) {
      return payload;
    }
    if (!payload || !Array.isArray(payload.results)) {
      return collected;
    }
    collected.push(...payload.results);
    nextParams = undefined;
    nextPath = safeNextPath(payload.next);
  }
  return collected;
}

function redirectToLogin() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  window.location.href = `${base}/login`;
}

// Request interceptor to add JWT token. Credential endpoints must not send a
// stale access token, or an expired token blocks login, logout, and refresh.
api.interceptors.request.use(
  (config) => {
    if (isUnauthenticatedPath(config.url)) {
      if (config.headers) {
        delete config.headers.Authorization;
      }
      return config;
    }
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

let refreshPromise = null;

// Response interceptor to handle token refresh and errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const url = original?.url || '';
    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !isUnauthenticatedPath(url) &&
      !isDemoMode()
    ) {
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        original._retry = true;
        try {
          if (!refreshPromise) {
            refreshPromise = api.post(REFRESH_PATH, { refresh }).finally(() => {
              refreshPromise = null;
            });
          }
          const response = await refreshPromise;
          const access = response.data?.access;
          if (!access) {
            throw new Error('Missing access token');
          }
          localStorage.setItem('access_token', access);
          if (response.data.refresh) {
            localStorage.setItem('refresh_token', response.data.refresh);
          }
          original.headers = original.headers || {};
          original.headers.Authorization = `Bearer ${access}`;
          return api(original);
        } catch (refreshError) {
          redirectToLogin();
          return Promise.reject(refreshError);
        }
      }
      redirectToLogin();
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  register: (data) => (isDemoMode() ? demoAuthAPI.register(data) : api.post('/auth/register/', data)),
  login: (email, password) =>
    isDemoMode() ? demoAuthAPI.login(email, password) : api.post('/auth/login/', { email, password }),
  logout: () => {
    if (isDemoMode()) {
      return demoAuthAPI.logout();
    }
    const refresh = localStorage.getItem('refresh_token');
    return api.post('/auth/logout/', { refresh });
  },
  getCurrentUser: () => (isDemoMode() ? demoAuthAPI.getCurrentUser() : api.get('/auth/users/me/')),
};

// Projects API calls
export const projectsAPI = {
  list: async () => {
    if (isDemoMode()) {
      return demoProjectsAPI.list();
    }
    return { data: await getAllPages('/projects/') };
  },
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
  list: async (params = {}) => {
    if (isDemoMode()) {
      return demoIssuesAPI.list(params);
    }
    return { data: await getAllPages('/issues/', params) };
  },
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
  list: async (params = {}) => {
    if (isDemoMode()) {
      return demoCommentsAPI.list(params);
    }
    return { data: await getAllPages('/comments/', params) };
  },
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
