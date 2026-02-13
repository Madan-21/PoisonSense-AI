import React, { useState, useEffect } from "react";
import api from "../api/axios";
import "../styles/BlogSubmissionReview.css";

const BlogSubmissionReview = () => {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchSubmissions();
  }, []);

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      const response = await api.get("/blog/submissions");
      setSubmissions(response.data || []);
    } catch (error) {
      console.error("Error fetching submissions:", error);
      setSubmissions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (submissionId, action) => {
    try {
      setActionLoading(true);
      await api.post(`/blog/submissions/${submissionId}/${action}`, { comment: null });
      // Refresh submissions
      await fetchSubmissions();
      setSelectedSubmission(null);
      alert(`Submission ${action}ed successfully!`);
    } catch (error) {
      console.error(`Error ${action}ing submission:`, error);
      alert(`Failed to ${action} submission: ${error.response?.data?.detail || error.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { color: "#ff9800", icon: "⏳", text: "Pending Review" },
      approved: { color: "#4caf50", icon: "✓", text: "Approved" },
      rejected: { color: "#f44336", icon: "✕", text: "Rejected" },
    };
    const badge = badges[status] || badges.pending;
    return (
      <span className="status-badge" style={{ background: badge.color }}>
        {badge.icon} {badge.text}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading submissions...</p>
      </div>
    );
  }

  return (
    <div className="blog-submission-review">
      {submissions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <h2>No Submissions Yet</h2>
          <p>Blog submissions will appear here for review</p>
        </div>
      ) : (
        <div className="submissions-container">
          <div className="submissions-list">
            <h2>Pending Submissions ({submissions.filter(s => s.status === "pending").length})</h2>
            {submissions.map((submission) => (
              <div
                key={submission.id}
                className={`submission-card ${selectedSubmission?.id === submission.id ? "selected" : ""}`}
                onClick={() => setSelectedSubmission(submission)}
              >
                <div className="submission-header">
                  <h3>{submission.title}</h3>
                  {getStatusBadge(submission.status)}
                </div>
                <div className="submission-meta">
                  <span className="meta-item">
                    📂 {submission.category}
                  </span>
                  <span className="meta-item">
                    👤 {submission.author_email}
                  </span>
                  <span className="meta-item">
                    📅 {formatDate(submission.created_at)}
                  </span>
                </div>
                <p className="submission-description">{submission.description}</p>
              </div>
            ))}
          </div>

          {selectedSubmission && (
            <div className="submission-detail">
              <div className="detail-header">
                <h2>Review Submission</h2>
                <button
                  className="close-btn"
                  onClick={() => setSelectedSubmission(null)}
                >
                  ✕
                </button>
              </div>

              <div className="detail-content">
                <div className="detail-section">
                  <h3>{selectedSubmission.title}</h3>
                  {getStatusBadge(selectedSubmission.status)}
                </div>

                <div className="detail-section">
                  <div className="detail-meta">
                    <div className="meta-row">
                      <strong>Category:</strong>
                      <span>{selectedSubmission.category}</span>
                    </div>
                    <div className="meta-row">
                      <strong>Author:</strong>
                      <span>{selectedSubmission.author_email}</span>
                    </div>
                    <div className="meta-row">
                      <strong>Submitted:</strong>
                      <span>{formatDate(selectedSubmission.created_at)}</span>
                    </div>
                  </div>
                </div>

                {selectedSubmission.featured_image && (
                  <div className="detail-section">
                    <strong>Featured Image:</strong>
                    <img
                      src={selectedSubmission.featured_image}
                      alt="Featured"
                      className="featured-preview"
                    />
                  </div>
                )}

                <div className="detail-section">
                  <strong>Description:</strong>
                  <p>{selectedSubmission.description}</p>
                </div>

                <div className="detail-section">
                  <strong>Content:</strong>
                  <div className="content-preview">
                    {selectedSubmission.content}
                  </div>
                </div>

                {selectedSubmission.status === "pending" && (
                  <div className="action-buttons">
                    <button
                      className="approve-btn"
                      onClick={() => handleAction(selectedSubmission.id, "approve")}
                      disabled={actionLoading}
                    >
                      {actionLoading ? "Processing..." : "✓ Approve & Publish"}
                    </button>
                    <button
                      className="reject-btn"
                      onClick={() => handleAction(selectedSubmission.id, "reject")}
                      disabled={actionLoading}
                    >
                      {actionLoading ? "Processing..." : "✕ Reject"}
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BlogSubmissionReview;
