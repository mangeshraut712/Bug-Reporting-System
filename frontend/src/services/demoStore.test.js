import { beforeEach, describe, expect, test } from 'vitest';
import {
  demoCommentsAPI,
  demoIssuesAPI,
  demoProjectsAPI,
  disableDemoMode,
  enableDemoMode,
  isDemoMode,
} from './demoStore';

describe('demo store', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('seeds projects and filters their issues', async () => {
    expect(isDemoMode()).toBe(false);
    enableDemoMode();
    expect(isDemoMode()).toBe(true);

    const projects = await demoProjectsAPI.list();
    expect(projects.data.map((project) => project.name)).toEqual([
      'Checkout Service',
      'Mobile App',
    ]);
    expect(projects.data[0].issue_count).toBe(3);

    const critical = await demoProjectsAPI.getIssues(1, { priority: 'critical' });
    expect(critical.data).toHaveLength(1);
    expect(critical.data[0].title).toBe('Apple Pay sheet dismisses on retry');

    const search = await demoProjectsAPI.getIssues(1, { search: 'tax row' });
    expect(search.data).toHaveLength(1);
    expect(search.data[0].status).toBe('closed');
  });

  test('creates a project, an issue, and a comment in the browser', async () => {
    enableDemoMode();

    const project = await demoProjectsAPI.create({
      name: 'Billing API',
      description: 'Invoices and receipts',
    });
    expect(project.data.issue_count).toBe(0);

    const issue = await demoIssuesAPI.createForProject(project.data.id, {
      title: 'Wrong tax',
      description: 'Tax is doubled',
      priority: 'high',
    });
    expect(issue.data.status).toBe('open');
    expect(issue.data.project_name).toBe('Billing API');

    const updated = await demoIssuesAPI.updateStatus(issue.data.id, 'closed');
    expect(updated.data.status).toBe('closed');

    const comment = await demoCommentsAPI.createForIssue(issue.data.id, {
      content: 'Shipped a fix',
    });
    expect(comment.data.author_email).toBe('demo@bugtracker.dev');

    const comments = await demoCommentsAPI.list({ issue_id: issue.data.id });
    expect(comments.data.map((item) => item.content)).toEqual(['Shipped a fix']);

    const stored = await demoIssuesAPI.retrieve(issue.data.id);
    expect(stored.data.comment_count).toBe(1);

    disableDemoMode();
    expect(isDemoMode()).toBe(false);
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  test('reseeds a corrupt demo store instead of crashing', async () => {
    localStorage.setItem('bugtracker_demo_store', '{');
    enableDemoMode();
    const projects = await demoProjectsAPI.list();
    expect(projects.data.map((project) => project.name)).toEqual([
      'Checkout Service',
      'Mobile App',
    ]);
  });

  test('rejects an update for a project that is not in the store', async () => {
    enableDemoMode();
    await expect(demoProjectsAPI.update(999, { name: 'Nope' })).rejects.toThrow(/not found/i);
  });
});
