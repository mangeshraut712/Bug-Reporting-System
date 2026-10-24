import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { asList, issuesAPI, projectsAPI } from '../services/api';
import { firstFieldError } from '../services/formErrors';
import { toast } from 'react-toastify';
import { Plus, AlertCircle } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';

const IssueListPage = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [searchText, setSearchText] = useState('');
  const [search, setSearch] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
  });
  const [submitting, setSubmitting] = useState(false);
  const requestId = useRef(0);

  useEffect(() => {
    const handle = setTimeout(() => setSearch(searchText.trim()), 200);
    return () => clearTimeout(handle);
  }, [searchText]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    projectsAPI
      .retrieve(projectId)
      .then((response) => {
        if (active) {
          setProject(response.data);
        }
      })
      .catch(() => {
        if (active) {
          toast.error('Failed to fetch data');
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  const loadIssues = useCallback(async () => {
    const current = requestId.current + 1;
    requestId.current = current;
    try {
      const issuesRes = await projectsAPI.getIssues(projectId, { status, priority, search });
      if (current === requestId.current) {
        setIssues(asList(issuesRes.data));
      }
    } catch (error) {
      if (current === requestId.current) {
        toast.error('Failed to fetch data');
      }
    }
  }, [projectId, status, priority, search]);

  useEffect(() => {
    loadIssues();
  }, [loadIssues]);

  const handleCreateIssue = async (e) => {
    e.preventDefault();
    if (submitting) {
      return;
    }
    try {
      setSubmitting(true);
      await issuesAPI.createForProject(projectId, formData);
      toast.success('Issue created successfully!');
      setFormData({ title: '', description: '', priority: 'medium' });
      setShowModal(false);
      loadIssues();
    } catch (error) {
      toast.error(firstFieldError(error.response?.data, 'Failed to create issue'));
    } finally {
      setSubmitting(false);
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'bg-blue-100 text-blue-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    };
    return colors[priority] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status) => {
    const colors = {
      open: 'bg-green-100 text-green-800',
      in_progress: 'bg-blue-100 text-blue-800',
      closed: 'bg-gray-100 text-gray-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <Link to="/dashboard" className="text-blue-600 hover:text-blue-700 mb-2 inline-block">
              ← Back to Projects
            </Link>
            <h1 className="text-4xl font-bold text-gray-900">{project?.name}</h1>
            <p className="text-gray-600 mt-2">{project?.description}</p>
          </div>
          <button
            type="button"
            onClick={() => setShowModal(true)}
            className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
          >
            <Plus size={20} />
            <span>New Issue</span>
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="issue-status-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                id="issue-status-filter"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-hidden"
              >
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="closed">Closed</option>
              </select>
            </div>
            <div>
              <label htmlFor="issue-priority-filter" className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                id="issue-priority-filter"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-hidden"
              >
                <option value="">All Priorities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label htmlFor="issue-search" className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <input
                id="issue-search"
                type="search"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="Search issues..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-hidden"
              />
            </div>
          </div>
        </div>

        {/* Issues List */}
        {issues.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <AlertCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No issues found</h3>
            <p className="text-gray-600">Create your first issue to get started</p>
          </div>
        ) : (
          <ul className="list-none space-y-4">
            {issues.map((issue) => (
              <li key={issue.id}>
                <Link
                  to={`/issues/${issue.id}`}
                  className="block bg-white rounded-lg shadow hover:shadow-lg transition p-6 cursor-pointer border border-gray-100"
                >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 hover:text-blue-600 wrap-break-word">
                      {issue.title}
                    </h3>
                    <p className="text-gray-600 text-sm mt-1 line-clamp-2 wrap-break-word">
                      {issue.description}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(issue.status)}`}>
                      {issue.status.replace('_', ' ')}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(issue.priority)}`}>
                      {issue.priority}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="space-x-4">
                    <span>Reporter: {issue.reporter_name}</span>
                    {issue.assignee_name && <span>Assignee: {issue.assignee_name}</span>}
                  </div>
                  <span>{new Date(issue.created_at).toLocaleDateString()}</span>
                </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Create Issue Modal */}
      {showModal && (
        <Modal title="Create New Issue" onClose={() => setShowModal(false)}>
            <form onSubmit={handleCreateIssue} className="space-y-4">
              <div>
                <label htmlFor="issue-title" className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  id="issue-title"
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-hidden"
                  placeholder="Issue title"
                />
              </div>
              <div>
                <label htmlFor="issue-description" className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  id="issue-description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                  rows="4"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-hidden"
                  placeholder="Issue description..."
                />
              </div>
              <div>
                <label htmlFor="issue-priority" className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select
                  id="issue-priority"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-hidden"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
        </Modal>
      )}
    </div>
  );
};

export default IssueListPage;
