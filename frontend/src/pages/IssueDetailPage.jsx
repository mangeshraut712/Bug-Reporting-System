import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { issuesAPI, commentsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import { ArrowLeft, MessageSquare, Send } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const IssueDetailPage = () => {
  const { issueId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [issue, setIssue] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [commentText, setCommentText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchIssueAndComments = useCallback(async () => {
    try {
      setLoading(true);
      const issueRes = await issuesAPI.retrieve(issueId);
      setIssue(issueRes.data);

      const commentsRes = await commentsAPI.list({ issue_id: issueId });
      setComments(commentsRes.data);
    } catch (error) {
      toast.error('Failed to fetch issue');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  }, [issueId, navigate]);

  useEffect(() => {
    fetchIssueAndComments();
  }, [fetchIssueAndComments]);

  const handleStatusChange = async (newStatus) => {
    try {
      const response = await issuesAPI.updateStatus(issueId, newStatus);
      setIssue(response.data);
      toast.success('Status updated successfully!');
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;

    try {
      setSubmitting(true);
      await commentsAPI.createForIssue(issueId, { content: commentText });
      toast.success('Comment added successfully!');
      setCommentText('');
      fetchIssueAndComments();
    } catch (error) {
      toast.error('Failed to add comment');
    } finally {
      setSubmitting(false);
    }
  };

  const canEditIssue = user && (user.id === issue?.reporter || user.id === issue?.assignee);

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
  if (!issue) return <div>Issue not found</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-6"
        >
          <ArrowLeft size={20} />
          <span>Back</span>
        </button>

        {/* Issue Details */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{issue.title}</h1>
              <p className="text-gray-600">{issue.description}</p>
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

          {/* Issue Metadata */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-6 border-t border-b">
            <div>
              <p className="text-sm text-gray-600">Project</p>
              <p className="font-medium text-gray-900">{issue.project_name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Reporter</p>
              <p className="font-medium text-gray-900">{issue.reporter_name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Assignee</p>
              <p className="font-medium text-gray-900">{issue.assignee_name || 'Unassigned'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Created</p>
              <p className="font-medium text-gray-900">{new Date(issue.created_at).toLocaleDateString()}</p>
            </div>
          </div>

          {/* Status Update */}
          {canEditIssue && (
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Update Status
              </label>
              <select
                value={issue.status}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              >
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="closed">Closed</option>
              </select>
            </div>
          )}
        </div>

        {/* Comments Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center space-x-2 mb-6">
            <MessageSquare size={24} className="text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">Comments ({issue.comment_count})</h2>
          </div>

          {/* Comments List */}
          <div className="space-y-4 mb-6">
            {comments.length === 0 ? (
              <p className="text-gray-600 text-center py-8">No comments yet. Be the first to comment!</p>
            ) : (
              comments.map((comment) => (
                <div key={comment.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-medium text-gray-900">{comment.author_name}</p>
                      <p className="text-sm text-gray-600">{comment.author_email}</p>
                    </div>
                    <p className="text-sm text-gray-500">{new Date(comment.created_at).toLocaleString()}</p>
                  </div>
                  <p className="text-gray-700">{comment.content}</p>
                </div>
              ))
            )}
          </div>

          {/* Add Comment Form */}
          <form onSubmit={handleAddComment} className="border-t pt-6">
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Add a comment
              </label>
              <textarea
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                rows="4"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                placeholder="Write your comment here..."
              />
            </div>
            <button
              type="submit"
              disabled={submitting || !commentText.trim()}
              className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
              <span>{submitting ? 'Posting...' : 'Post Comment'}</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default IssueDetailPage;
