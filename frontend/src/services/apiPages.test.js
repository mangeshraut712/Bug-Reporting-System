import { beforeEach, describe, expect, test, vi } from 'vitest';
import { authAPI, projectsAPI } from './api';

const apiMock = vi.hoisted(() => ({
  interceptors: {
    request: { use: vi.fn() },
    response: { use: vi.fn() },
  },
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
}));

vi.mock('axios', () => ({
  default: {
    create: () => apiMock,
  },
}));

describe('paginated API client', () => {
  beforeEach(() => {
    localStorage.clear();
    apiMock.get.mockReset();
    apiMock.post.mockReset();
  });

  test('follows a same-origin next page and ignores a foreign one', async () => {
    apiMock.get.mockImplementation((url) => {
      if (url === '/projects/') {
        return Promise.resolve({
          data: {
            count: 2,
            next: 'http://localhost:8000/api/projects/?page=2',
            results: [{ id: 1, name: 'First' }],
          },
        });
      }
      if (url === '/api/projects/?page=2') {
        return Promise.resolve({
          data: {
            count: 2,
            next: 'https://evil.example/api/projects/?page=3',
            results: [{ id: 2, name: 'Second' }],
          },
        });
      }
      return Promise.reject(new Error(`unexpected ${url}`));
    });

    const response = await projectsAPI.list();

    expect(response.data).toEqual([
      { id: 1, name: 'First' },
      { id: 2, name: 'Second' },
    ]);
    expect(apiMock.get).toHaveBeenCalledTimes(2);
  });

  test('sends the refresh token when logging out', async () => {
    localStorage.setItem('refresh_token', 'refresh-1');
    apiMock.post.mockResolvedValue({ data: { detail: 'Successfully logged out.' } });

    await authAPI.logout();

    expect(apiMock.post).toHaveBeenCalledWith('/auth/logout/', { refresh: 'refresh-1' });
  });
});
