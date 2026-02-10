import React, { useState, useEffect } from "react";
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
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/v1/blog/submissions", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSubmissions(data);
      } else {
        console.error("Failed to fetch submissions");
        // Mock data for development
        setSubmissions([
          {
            id: 1,
            title: "Understanding Pesticide Safety in Agriculture",
            category: "Prevention",
            author_email: "farmer@example.com",
            description: "A comprehensive guide on safe pesticide handling practices for farmers",
            content: "Pesticides are essential tools in modern agriculture, but they require careful handling...",
            status: "pending",
            created_at: "2024-01-20T10:30:00",
            featured_image: null,
          },
          {
            id: 2,
            title: "First Aid for Snake Bites: What You Should Know",
            category: "First Aid",
            author_email: "doctor@hospital.com",
            description: "Essential first aid steps for snake bite victims",
            content: "Snake bites can be life-threatening emergencies. Here's what you need to know...",
            status: "pending",
            created_at: "2024-01-21T14:15:00",
            featured_image: null,
          },
        ]);
      }
    } catch (error) {
      console.error("Error fetching submissions:", error);
      // Mock data for development
      setSubmissions([
        {
          id: 1,
          title: "Understanding Pesticide Safety in Agriculture",
          category: "Prevention",
          author_email: "farmer@example.com",
          description: "A comprehensive guide on safe pesticide handling practices for farmers",
          content: "Pesticides are essential tools in modern agriculture, but they require careful handling...",
          status: "pending",
          created_at: "2024-01-20T10:30:00",
          featured_image: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (submissionId, action) => {
    try {
      setActionLoading(true);
      const token = localStorage.getItem("access_token");
      const response = await fetch(`/api/v1/blog/submissions/${submissionId}/${action}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ comment: null })
      });

      if (response.ok) {
        // Refresh submissions
        await fetchSubmissions();
        setSelectedSubmission(null);
        alert(`Submission ${action}ed successfully!`);
      } else {
        alert(`Failed to ${action} submission`);
      }
    } catch (error) {
      console.error(`Error ${action}ing submission:`, error);
      alert(`Error: ${error.message}`);
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
