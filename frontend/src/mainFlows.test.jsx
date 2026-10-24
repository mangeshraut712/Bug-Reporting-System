import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import App from './App';

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

const renderAt = (path) => {
  window.history.pushState({}, '', path);
  return render(<App />);
};

describe('main flows', () => {
  beforeEach(() => {
    localStorage.clear();
    apiMock.get.mockReset();
    apiMock.post.mockReset();
    apiMock.patch.mockReset();
    apiMock.delete.mockReset();
  });

  test('sends an anonymous visitor from the home page to sign in', async () => {
    renderAt('/');

    expect(await screen.findByRole('heading', { name: 'Bug Tracker' })).toBeInTheDocument();
    expect(screen.getByLabelText('Email Address')).toBeRequired();
    expect(screen.getByLabelText('Password')).toHaveAttribute('autocomplete', 'current-password');
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /explore demo workspace/i })).toBeInTheDocument();
  });

  test('keeps the dashboard behind sign-in', async () => {
    renderAt('/dashboard');

    expect(await screen.findByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Projects' })).not.toBeInTheDocument();
  });

  test('opens the mobile navigation links', async () => {
    const user = userEvent.setup();
    renderAt('/login');

    const menuButton = screen.getByRole('button', { name: 'Open menu' });
    expect(menuButton).toHaveAttribute('aria-expanded', 'false');
    expect(screen.getAllByRole('link', { name: 'Register' })).toHaveLength(1);

    await user.click(menuButton);

    expect(menuButton).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getAllByRole('link', { name: 'Register' })).toHaveLength(2);
    expect(screen.getAllByRole('link', { name: 'Login' })).toHaveLength(2);
  });

  test('rejects a sign-in the API refuses', async () => {
    const user = userEvent.setup();
    apiMock.post.mockRejectedValueOnce({
      response: { status: 401, data: { detail: 'Invalid credentials' } },
    });
    renderAt('/login');

    await user.type(screen.getByPlaceholderText('you@example.com'), 'ada@example.com');
    await user.type(screen.getByPlaceholderText('••••••••'), 'wrong-password');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(await screen.findByText('Invalid email or password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
  });

  test('signs in against the API and shows an empty project list', async () => {
    const user = userEvent.setup();
    apiMock.post.mockResolvedValueOnce({
      data: { access: 'access-token', refresh: 'refresh-token' },
    });
    apiMock.get.mockImplementation((url) => {
      if (url === '/auth/users/me/') {
        return Promise.resolve({
          data: { id: 9, email: 'ada@example.com', first_name: 'Ada', username: 'ada' },
        });
      }
      if (url === '/projects/') {
        return Promise.resolve({ data: [] });
      }
      return Promise.reject(new Error(`unexpected ${url}`));
    });
    renderAt('/login');

    await user.type(screen.getByPlaceholderText('you@example.com'), 'ada@example.com');
    await user.type(screen.getByPlaceholderText('••••••••'), 'correct-password');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(await screen.findByRole('heading', { name: 'Projects' })).toBeInTheDocument();
    expect(screen.getByText(/welcome, ada/i)).toBeInTheDocument();
    expect(screen.getByText('No projects yet')).toBeInTheDocument();
    expect(localStorage.getItem('access_token')).toBe('access-token');
  });

  test('renders a paginated project list from the API', async () => {
    const user = userEvent.setup();
    apiMock.post.mockResolvedValueOnce({
      data: { access: 'access-token', refresh: 'refresh-token' },
    });
    apiMock.get.mockImplementation((url) => {
      if (url === '/auth/users/me/') {
        return Promise.resolve({
          data: { id: 9, email: 'ada@example.com', first_name: 'Ada', username: 'ada' },
        });
      }
      if (url === '/projects/') {
        return Promise.resolve({
          data: {
            count: 1,
            next: null,
            results: [
              {
                id: 4,
                name: 'Paged Project',
                description: 'Returned inside a DRF page',
                issue_count: 2,
                created_at: '2026-01-15T00:00:00Z',
              },
            ],
          },
        });
      }
      return Promise.reject(new Error(`unexpected ${url}`));
    });
    renderAt('/login');

    await user.type(screen.getByPlaceholderText('you@example.com'), 'ada@example.com');
    await user.type(screen.getByPlaceholderText('••••••••'), 'correct-password');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(await screen.findByText('Paged Project')).toBeInTheDocument();
    expect(screen.getByText('Returned inside a DRF page')).toBeInTheDocument();
    expect(screen.getByText('2 issues')).toBeInTheDocument();
  });

  test('stops registration when the passwords do not match', async () => {
    const user = userEvent.setup();
    renderAt('/login');

    await user.click(screen.getByRole('link', { name: 'Register here' }));
    expect(await screen.findByRole('heading', { name: 'Bug Tracker' })).toBeInTheDocument();
    expect(screen.getByText('Create your account')).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText('you@example.com'), 'new@example.com');
    await user.type(screen.getByPlaceholderText('username'), 'newuser');
    const [password, confirm] = screen.getAllByPlaceholderText('••••••••');
    await user.type(password, 'long-password');
    await user.type(confirm, 'different-password');
    await user.click(screen.getByRole('button', { name: /create account/i }));

    expect(await screen.findByText('Passwords do not match')).toBeInTheDocument();
    expect(apiMock.post).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  test('registers an account and returns to sign in', async () => {
    const user = userEvent.setup();
    apiMock.post.mockResolvedValueOnce({
      data: { email: 'new@example.com', username: 'newuser' },
    });
    renderAt('/register');

    await user.type(screen.getByPlaceholderText('you@example.com'), 'new@example.com');
    await user.type(screen.getByPlaceholderText('username'), 'newuser');
    await user.type(screen.getByPlaceholderText('John'), 'New');
    await user.type(screen.getByPlaceholderText('Doe'), 'User');
    const [password, confirm] = screen.getAllByPlaceholderText('••••••••');
    await user.type(password, 'long-password');
    await user.type(confirm, 'long-password');
    await user.click(screen.getByRole('button', { name: /create account/i }));

    expect(await screen.findByText('Registration successful! Please log in.')).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    expect(apiMock.post).toHaveBeenCalledWith(
      '/auth/register/',
      expect.objectContaining({
        email: 'new@example.com',
        username: 'newuser',
        first_name: 'New',
        last_name: 'User',
      })
    );
  });

  test('shows the field error when registration is rejected', async () => {
    const user = userEvent.setup();
    apiMock.post.mockRejectedValueOnce({
      response: { status: 400, data: { email: ['A user with this email already exists.'] } },
    });
    renderAt('/register');

    await user.type(screen.getByLabelText('Email Address'), 'ada@example.com');
    await user.type(screen.getByLabelText('Username'), 'ada');
    const [password, confirm] = screen.getAllByPlaceholderText('••••••••');
    await user.type(password, 'long-password');
    await user.type(confirm, 'long-password');
    await user.click(screen.getByRole('button', { name: /create account/i }));

    expect(await screen.findByText('A user with this email already exists.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  test('walks the demo workspace from projects through a comment', async () => {
    const user = userEvent.setup();
    renderAt('/login');

    await user.click(screen.getByRole('button', { name: /explore demo workspace/i }));

    expect(await screen.findByRole('heading', { name: 'Projects' })).toBeInTheDocument();
    expect(screen.getByText('Checkout Service')).toBeInTheDocument();
    expect(screen.getByText('Mobile App')).toBeInTheDocument();
    expect(screen.getByText(/welcome, alex/i)).toBeInTheDocument();
    expect(screen.getByText('Demo')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /new project/i }));
    expect(screen.getByRole('dialog', { name: 'Create New Project' })).toBeInTheDocument();
    await user.type(screen.getByPlaceholderText('My Project'), 'Billing API');
    await user.type(screen.getByPlaceholderText('Project description...'), 'Invoices and receipts');
    await user.click(screen.getByRole('button', { name: 'Create' }));

    expect(await screen.findByText('Billing API')).toBeInTheDocument();
    expect(screen.getByText('Invoices and receipts')).toBeInTheDocument();

    await user.click(screen.getByRole('link', { name: /checkout service/i }));
    expect(await screen.findByRole('heading', { name: 'Checkout Service' })).toBeInTheDocument();
    expect(screen.getByText('Promo codes fail on guest checkout')).toBeInTheDocument();

    const [statusFilter] = screen.getAllByRole('combobox');
    await user.selectOptions(statusFilter, 'closed');
    expect(await screen.findByText('Receipt email missing tax line')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByText('Promo codes fail on guest checkout')).not.toBeInTheDocument();
    });

    await user.selectOptions(screen.getAllByRole('combobox')[0], '');
    expect(await screen.findByText('Promo codes fail on guest checkout')).toBeInTheDocument();
    await user.type(screen.getByPlaceholderText('Search issues...'), 'Apple Pay');
    await waitFor(() => {
      expect(screen.getByText('Apple Pay sheet dismisses on retry')).toBeInTheDocument();
      expect(screen.queryByText('Receipt email missing tax line')).not.toBeInTheDocument();
    });

    await user.clear(screen.getByPlaceholderText('Search issues...'));
    expect(await screen.findByText('Promo codes fail on guest checkout')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /new issue/i }));
    await user.type(screen.getByPlaceholderText('Issue title'), 'Wrong tax');
    await user.type(screen.getByPlaceholderText('Issue description...'), 'Tax is doubled');
    await user.selectOptions(screen.getAllByRole('combobox').at(-1), 'critical');
    await user.click(screen.getByRole('button', { name: 'Create' }));

    const createdIssue = await screen.findByRole('link', { name: /wrong tax/i });
    expect(createdIssue).toHaveTextContent('Tax is doubled');
    expect(createdIssue).toHaveTextContent('critical');

    await user.click(screen.getByRole('link', { name: /promo codes fail/i }));
    expect(await screen.findByRole('heading', { name: /promo codes fail on guest checkout/i })).toBeInTheDocument();
    expect(screen.getByText(/reproduced on staging/i)).toBeInTheDocument();
    expect(screen.getByText('Comments (2)')).toBeInTheDocument();

    await user.selectOptions(screen.getByRole('combobox'), 'in_progress');
    expect(await screen.findByText('in progress')).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText('Write your comment here...'), 'Shipped a fix');
    await user.click(screen.getByRole('button', { name: /post comment/i }));
    expect(await screen.findByText('Shipped a fix')).toBeInTheDocument();
    expect(screen.getByText('Comments (3)')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /logout/i }));
    expect(await screen.findByRole('button', { name: 'Sign In' })).toBeInTheDocument();
    expect(screen.queryByText(/welcome, alex/i)).not.toBeInTheDocument();
    expect(localStorage.getItem('demo_mode')).toBeNull();
  });

  test('lets a project owner update status on an issue they did not report', async () => {
    const user = userEvent.setup();
    localStorage.setItem('access_token', 'access-token');
    apiMock.get.mockImplementation((url) => {
      if (url === '/auth/users/me/') {
        return Promise.resolve({
          data: { id: 9, email: 'ada@example.com', first_name: 'Ada', username: 'ada' },
        });
      }
      if (url === '/issues/7/') {
        return Promise.resolve({
          data: {
            id: 7,
            title: 'Owned by Ada',
            description: 'Filed by someone else',
            status: 'open',
            priority: 'low',
            project_name: 'Checkout Service',
            project_created_by: 9,
            reporter: 3,
            reporter_name: 'Other Person',
            assignee: null,
            assignee_name: null,
            created_at: '2026-01-15T00:00:00Z',
            comment_count: 0,
          },
        });
      }
      if (url === '/comments/') {
        return Promise.resolve({ data: [] });
      }
      return Promise.reject(new Error(`unexpected ${url}`));
    });
    apiMock.patch.mockResolvedValue({
      data: {
        id: 7,
        title: 'Owned by Ada',
        description: 'Filed by someone else',
        status: 'closed',
        priority: 'low',
        project_name: 'Checkout Service',
        project_created_by: 9,
        reporter: 3,
        reporter_name: 'Other Person',
        assignee: null,
        created_at: '2026-01-15T00:00:00Z',
        comment_count: 0,
      },
    });
    renderAt('/issues/7');

    expect(await screen.findByRole('heading', { name: 'Owned by Ada' })).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText('Update Status'), 'closed');
    expect(await screen.findByText('closed')).toBeInTheDocument();
    expect(apiMock.patch).toHaveBeenCalledWith('/issues/7/update_status/', { status: 'closed' });
  });
});
