import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { asList, projectsAPI } from '../services/api';
import { firstFieldError } from '../services/formErrors';
import { toast } from 'react-toastify';
import { Plus, Folder } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';

const DashboardPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await projectsAPI.list();
      setProjects(asList(response.data));
    } catch (error) {
      toast.error('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (submitting) {
      return;
    }
    try {
      setSubmitting(true);
      await projectsAPI.create(formData);
      toast.success('Project created successfully!');
      setFormData({ name: '', description: '' });
      setShowModal(false);
      fetchProjects();
    } catch (error) {
      toast.error(firstFieldError(error.response?.data, 'Failed to create project'));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Projects</h1>
            <p className="text-gray-600 mt-2">Open a project to filter, create, and track issues</p>
          </div>
          <button
            type="button"
            onClick={() => setShowModal(true)}
            className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
          >
            <Plus size={20} />
            <span>New Project</span>
          </button>
        </div>

        {projects.length === 0 ? (
          <div className="text-center py-12">
            <Folder className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
            <p className="text-gray-600 mb-6">Create your first project to get started</p>
            <button
              type="button"
              onClick={() => setShowModal(true)}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Create Project
            </button>
          </div>
        ) : (
          <ul className="grid list-none grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <li key={project.id}>
                <Link
                  to={`/projects/${project.id}/issues`}
                  className="block bg-white rounded-lg shadow hover:shadow-lg transition p-6 cursor-pointer border border-gray-100"
                >
                <div className="flex items-start justify-between mb-4">
                  <Folder className="text-blue-600" size={32} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2 wrap-break-word">{project.name}</h3>
                <p className="text-gray-600 text-sm mb-4 line-clamp-2 wrap-break-word">{project.description}</p>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>
                    {project.issue_count} {project.issue_count === 1 ? 'issue' : 'issues'}
                  </span>
                  <span>{new Date(project.created_at).toLocaleDateString()}</span>
                </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Create Project Modal */}
      {showModal && (
        <Modal title="Create New Project" onClose={() => setShowModal(false)}>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label htmlFor="project-name" className="block text-sm font-medium text-gray-700 mb-1">
                  Project Name
                </label>
                <input
                  id="project-name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-hidden"
                  placeholder="My Project"
                />
              </div>
              <div>
                <label htmlFor="project-description" className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  id="project-description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                  rows="4"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-hidden"
                  placeholder="Project description..."
                />
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

export default DashboardPage;
