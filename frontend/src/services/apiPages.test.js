import { beforeEach, describe, expect, test, vi } from 'vitest';
import { MAX_LIST_PAGES, authAPI, nextPagePath, projectsAPI } from './api';

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
      if (url === '/projects/?page=2') {
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
    expect(apiMock.get).toHaveBeenNthCalledWith(2, '/projects/?page=2', undefined);
  });

  test('keeps next links relative to the API base path', () => {
    expect(nextPagePath('http://localhost:8000/api/projects/?page=2', 'http://localhost:8000/api')).toBe(
      '/projects/?page=2'
    );
    expect(nextPagePath('https://evil.example/api/projects/?page=3', 'http://localhost:8000/api')).toBeNull();
    expect(nextPagePath('http://localhost:8000/admin/', 'http://localhost:8000/api')).toBeNull();
  });

  test('stops when a next link repeats', async () => {
    apiMock.get.mockImplementation((url) => {
      if (url === '/projects/') {
        return Promise.resolve({
          data: {
            next: 'http://localhost:8000/api/projects/?page=2',
            results: [{ id: 1 }],
          },
        });
      }
      return Promise.resolve({
        data: {
          next: 'http://localhost:8000/api/projects/?page=2',
          results: [{ id: 2 }],
        },
      });
    });

    await expect(projectsAPI.list()).rejects.toThrow(/did not advance/i);
  });

  test('rejects a list that never ends', async () => {
    apiMock.get.mockImplementation((url) => {
      const page = url === '/projects/' ? 1 : Number(new URL(url, 'http://localhost').searchParams.get('page'));
      return Promise.resolve({
        data: {
          next: `http://localhost:8000/api/projects/?page=${page + 1}`,
          results: [{ id: page }],
        },
      });
    });

    await expect(projectsAPI.list()).rejects.toThrow(/too many pages/i);
    expect(apiMock.get).toHaveBeenCalledTimes(MAX_LIST_PAGES);
  });

  test('sends the refresh token when logging out', async () => {
    localStorage.setItem('refresh_token', 'refresh-1');
    apiMock.post.mockResolvedValue({ data: { detail: 'Successfully logged out.' } });

    await authAPI.logout();

    expect(apiMock.post).toHaveBeenCalledWith('/auth/logout/', { refresh: 'refresh-1' });
  });
});
