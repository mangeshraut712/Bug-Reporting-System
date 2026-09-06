const STORAGE_KEY = 'bugtracker_demo_store';
export const DEMO_MODE_KEY = 'demo_mode';

export const DEMO_USER = {
  id: 1,
  email: 'demo@bugtracker.dev',
  username: 'demo',
  first_name: 'Alex',
  last_name: 'Chen',
};

const now = () => new Date().toISOString();

const seedStore = () => ({
  nextProjectId: 3,
  nextIssueId: 5,
  nextCommentId: 4,
  projects: [
    {
      id: 1,
      name: 'Checkout Service',
      description: 'Payments, cart, and order confirmation flows for the storefront.',
      created_at: '2026-08-12T14:20:00.000Z',
    },
    {
      id: 2,
      name: 'Mobile App',
      description: 'iOS and Android client issues, crash reports, and release blockers.',
      created_at: '2026-08-28T09:05:00.000Z',
    },
  ],
  issues: [
    {
      id: 1,
      project: 1,
      project_name: 'Checkout Service',
      title: 'Promo codes fail on guest checkout',
      description:
        'Applying a valid promo code on guest checkout returns 500 and the order total never updates.',
      status: 'open',
      priority: 'high',
      reporter: 1,
      reporter_name: 'Alex Chen',
      assignee: 1,
      assignee_name: 'Alex Chen',
      created_at: '2026-09-01T11:30:00.000Z',
      comment_count: 2,
    },
    {
      id: 2,
      project: 1,
      project_name: 'Checkout Service',
      title: 'Apple Pay sheet dismisses on retry',
      description:
        'After a declined card, retrying Apple Pay closes the sheet instead of prompting again.',
      status: 'in_progress',
      priority: 'critical',
      reporter: 1,
      reporter_name: 'Alex Chen',
      assignee: 1,
      assignee_name: 'Alex Chen',
      created_at: '2026-09-03T16:12:00.000Z',
      comment_count: 1,
    },
    {
      id: 3,
      project: 1,
      project_name: 'Checkout Service',
      title: 'Receipt email missing tax line',
      description: 'Order confirmation emails omit the tax row for US-CA addresses.',
      status: 'closed',
      priority: 'medium',
      reporter: 1,
      reporter_name: 'Alex Chen',
      assignee: null,
      assignee_name: null,
      created_at: '2026-08-18T08:40:00.000Z',
      comment_count: 0,
    },
    {
      id: 4,
      project: 2,
      project_name: 'Mobile App',
      title: 'Crash on cold start after logout',
      description: 'Android 14 devices crash in AuthStore when the refresh token is already cleared.',
      status: 'open',
      priority: 'low',
      reporter: 1,
      reporter_name: 'Alex Chen',
      assignee: null,
      assignee_name: null,
      created_at: '2026-09-05T19:22:00.000Z',
      comment_count: 0,
    },
  ],
  comments: [
    {
      id: 1,
      issue: 1,
      author_name: 'Alex Chen',
      author_email: 'demo@bugtracker.dev',
      content: 'Reproduced on staging. Stack trace points at CouponService.apply().',
      created_at: '2026-09-01T13:05:00.000Z',
    },
    {
      id: 2,
      issue: 1,
      author_name: 'Alex Chen',
      author_email: 'demo@bugtracker.dev',
      content: 'Fix in review: skip guest user lookup when no account exists.',
      created_at: '2026-09-02T10:18:00.000Z',
    },
    {
      id: 3,
      issue: 2,
      author_name: 'Alex Chen',
      author_email: 'demo@bugtracker.dev',
      content: 'Happens only when the first attempt is declined by the bank.',
      created_at: '2026-09-03T17:40:00.000Z',
    },
  ],
});

const withIssueCounts = (store) =>
  store.projects.map((project) => ({
    ...project,
    issue_count: store.issues.filter((issue) => issue.project === project.id).length,
  }));

export const isDemoMode = () =>
  typeof window !== 'undefined' && localStorage.getItem(DEMO_MODE_KEY) === 'true';

export const enableDemoMode = () => {
  localStorage.setItem(DEMO_MODE_KEY, 'true');
  localStorage.setItem('access_token', 'demo-token');
  if (!localStorage.getItem(STORAGE_KEY)) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(seedStore()));
  }
};

export const disableDemoMode = () => {
  localStorage.removeItem(DEMO_MODE_KEY);
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

const readStore = () => {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    const seeded = seedStore();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(seeded));
    return seeded;
  }
  return JSON.parse(raw);
};

const writeStore = (store) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
};

const wrap = (data) => Promise.resolve({ data });

export const demoAuthAPI = {
  register: () => wrap(DEMO_USER),
  login: () => wrap({ access: 'demo-token', refresh: 'demo-refresh' }),
  logout: () => wrap({ detail: 'ok' }),
  getCurrentUser: () => wrap(DEMO_USER),
};

export const demoProjectsAPI = {
  list: () => wrap(withIssueCounts(readStore())),
  create: (data) => {
    const store = readStore();
    const project = {
      id: store.nextProjectId,
      name: data.name,
      description: data.description,
      created_at: now(),
    };
    store.nextProjectId += 1;
    store.projects.unshift(project);
    writeStore(store);
    return wrap({ ...project, issue_count: 0 });
  },
  retrieve: (id) => {
    const store = readStore();
    const project = withIssueCounts(store).find((item) => String(item.id) === String(id));
    if (!project) {
      return Promise.reject(new Error('Project not found'));
    }
    return wrap(project);
  },
  update: (id, data) => {
    const store = readStore();
    const index = store.projects.findIndex((item) => String(item.id) === String(id));
    store.projects[index] = { ...store.projects[index], ...data };
    writeStore(store);
    return wrap(store.projects[index]);
  },
  delete: (id) => {
    const store = readStore();
    store.projects = store.projects.filter((item) => String(item.id) !== String(id));
    writeStore(store);
    return wrap(null);
  },
  getIssues: (id, params = {}) => {
    const store = readStore();
    let issues = store.issues.filter((issue) => String(issue.project) === String(id));
    if (params.status) {
      issues = issues.filter((issue) => issue.status === params.status);
    }
    if (params.priority) {
      issues = issues.filter((issue) => issue.priority === params.priority);
    }
    if (params.search) {
      const query = params.search.toLowerCase();
      issues = issues.filter(
        (issue) =>
          issue.title.toLowerCase().includes(query) ||
          issue.description.toLowerCase().includes(query)
      );
    }
    return wrap(issues);
  },
};

export const demoIssuesAPI = {
  list: (params = {}) => {
    const store = readStore();
    let issues = store.issues;
    if (params.search) {
      const query = params.search.toLowerCase();
      issues = issues.filter((issue) => issue.title.toLowerCase().includes(query));
    }
    return wrap(issues);
  },
  create: (data) => demoIssuesAPI.createForProject(data.project, data),
  retrieve: (id) => {
    const store = readStore();
    const issue = store.issues.find((item) => String(item.id) === String(id));
    if (!issue) {
      return Promise.reject(new Error('Issue not found'));
    }
    return wrap({
      ...issue,
      comment_count: store.comments.filter((comment) => comment.issue === issue.id).length,
    });
  },
  update: (id, data) => {
    const store = readStore();
    const index = store.issues.findIndex((item) => String(item.id) === String(id));
    store.issues[index] = { ...store.issues[index], ...data };
    writeStore(store);
    return wrap(store.issues[index]);
  },
  delete: (id) => {
    const store = readStore();
    store.issues = store.issues.filter((item) => String(item.id) !== String(id));
    writeStore(store);
    return wrap(null);
  },
  createForProject: (projectId, data) => {
    const store = readStore();
    const project = store.projects.find((item) => String(item.id) === String(projectId));
    const issue = {
      id: store.nextIssueId,
      project: Number(projectId),
      project_name: project?.name || 'Project',
      title: data.title,
      description: data.description,
      status: 'open',
      priority: data.priority || 'medium',
      reporter: DEMO_USER.id,
      reporter_name: `${DEMO_USER.first_name} ${DEMO_USER.last_name}`,
      assignee: null,
      assignee_name: null,
      created_at: now(),
      comment_count: 0,
    };
    store.nextIssueId += 1;
    store.issues.unshift(issue);
    writeStore(store);
    return wrap(issue);
  },
  updateStatus: (id, status) => {
    const store = readStore();
    const index = store.issues.findIndex((item) => String(item.id) === String(id));
    store.issues[index] = { ...store.issues[index], status };
    writeStore(store);
    return wrap(store.issues[index]);
  },
  assign: (id, assigneeId) => {
    const store = readStore();
    const index = store.issues.findIndex((item) => String(item.id) === String(id));
    store.issues[index] = {
      ...store.issues[index],
      assignee: assigneeId,
      assignee_name: assigneeId ? `${DEMO_USER.first_name} ${DEMO_USER.last_name}` : null,
    };
    writeStore(store);
    return wrap(store.issues[index]);
  },
};

export const demoCommentsAPI = {
  list: (params = {}) => {
    const store = readStore();
    let comments = store.comments;
    if (params.issue_id) {
      comments = comments.filter((comment) => String(comment.issue) === String(params.issue_id));
    }
    return wrap(comments);
  },
  create: (data) => demoCommentsAPI.createForIssue(data.issue, data),
  retrieve: (id) => {
    const store = readStore();
    return wrap(store.comments.find((item) => String(item.id) === String(id)));
  },
  update: (id, data) => {
    const store = readStore();
    const index = store.comments.findIndex((item) => String(item.id) === String(id));
    store.comments[index] = { ...store.comments[index], ...data };
    writeStore(store);
    return wrap(store.comments[index]);
  },
  delete: (id) => {
    const store = readStore();
    store.comments = store.comments.filter((item) => String(item.id) !== String(id));
    writeStore(store);
    return wrap(null);
  },
  createForIssue: (issueId, data) => {
    const store = readStore();
    const comment = {
      id: store.nextCommentId,
      issue: Number(issueId),
      author_name: `${DEMO_USER.first_name} ${DEMO_USER.last_name}`,
      author_email: DEMO_USER.email,
      content: data.content,
      created_at: now(),
    };
    store.nextCommentId += 1;
    store.comments.push(comment);
    const issue = store.issues.find((item) => String(item.id) === String(issueId));
    if (issue) {
      issue.comment_count = (issue.comment_count || 0) + 1;
    }
    writeStore(store);
    return wrap(comment);
  },
};
