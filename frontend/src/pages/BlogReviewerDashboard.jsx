import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/BlogReviewerDashboard.css";

export default function BlogReviewerDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [filter, setFilter] = useState("");
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [reviewComment, setReviewComment] = useState("");
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchSubmissions();
  }, [filter]);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get("/dashboard/blog-reviewer");
      setDashboardData(response.data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      if (error.response?.status === 403) {
        alert("You don't have blog reviewer privileges");
        navigate("/dashboard");
      }
    }
  };

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      const url = filter ? `/blog/submissions?status_filter=${filter}` : `/blog/submissions`;
      const response = await api.get(url);
      setSubmissions(response.data);
    } catch (error) {
      console.error("Error fetching submissions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (submissionId) => {
    if (!confirm("Are you sure you want to approve this blog article?")) return;

    try {
      setProcessing(true);
      await api.post(`/blog/submissions/${submissionId}/approve`, {
        comment: reviewComment || "Approved"
      });
      alert("✅ Blog article approved successfully!");
      setReviewComment("");
      setSelectedSubmission(null);
      fetchSubmissions();
      fetchDashboardData();
    } catch (error) {
      console.error("Error approving submission:", error);
      alert("Failed to approve submission: " + (error.response?.data?.detail || error.message));
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async (submissionId) => {
    if (!reviewComment.trim()) {
      alert("Please provide a reason for rejection");
      return;
    }

    if (!confirm("Are you sure you want to reject this blog article?")) return;

    try {
      setProcessing(true);
      await api.post(`/blog/submissions/${submissionId}/reject`, {
        comment: reviewComment
      });
      alert("❌ Blog article rejected");
      setReviewComment("");
      setSelectedSubmission(null);
      fetchSubmissions();
      fetchDashboardData();
    } catch (error) {
      console.error("Error rejecting submission:", error);
      alert("Failed to reject submission: " + (error.response?.data?.detail || error.message));
    } finally {
      setProcessing(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  return (
    <>
      <Navbar />
      <div className="blog-reviewer-dashboard">
        <div className="reviewer-header">
          <h1>📝 Blog Review Dashboard</h1>
          <p>Review and moderate blog submissions</p>
        </div>

        {/* Statistics Cards */}
        {dashboardData && (
          <div className="stats-grid">
            <div className="stat-card pending">
              <div className="stat-icon">⏳</div>
              <div className="stat-info">
                <h3>{dashboardData.review_stats?.pending_submissions || 0}</h3>
                <p>Pending Reviews</p>
              </div>
            </div>
            <div className="stat-card reviewed">
              <div className="stat-icon">✅</div>
              <div className="stat-info">
                <h3>{dashboardData.review_stats?.total_reviewed || 0}</h3>
                <p>Total Reviewed</p>
              </div>
            </div>
            <div className="stat-card info">
              <div className="stat-icon">👤</div>
              <div className="stat-info">
                <h3>{dashboardData.reviewer_info?.name}</h3>
                <p>Reviewer</p>
              </div>
            </div>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="filter-tabs">
          <button
            className={`filter-btn ${filter === "pending" ? "active" : ""}`}
            onClick={() => setFilter("pending")}
          >
            ⏳ Pending ({dashboardData?.review_stats?.pending_submissions || 0})
          </button>
          <button
            className={`filter-btn ${filter === "approved" ? "active" : ""}`}
            onClick={() => setFilter("approved")}
          >
            ✅ Approved
          </button>
          <button
            className={`filter-btn ${filter === "rejected" ? "active" : ""}`}
            onClick={() => setFilter("rejected")}
          >
            ❌ Rejected
          </button>
          <button
            className={`filter-btn ${filter === "" ? "active" : ""}`}
            onClick={() => setFilter("")}
          >
            📋 All Submissions
          </button>
        </div>

        {/* Submissions List */}
        <div className="submissions-section">
          {loading ? (
            <div className="loading">Loading submissions...</div>
          ) : submissions.length === 0 ? (
            <div className="no-submissions">
              <p>📭 No submissions found</p>
            </div>
          ) : (
            <div className="submissions-grid">
              {submissions.map((submission) => (
                <div key={submission.id} className={`submission-card ${submission.status}`}>
                  <div className="submission-header">
                    <h3>{submission.title}</h3>
                    <span className={`status-badge ${submission.status}`}>
                      {submission.status === "pending" && "⏳"}
                      {submission.status === "approved" && "✅"}
                      {submission.status === "rejected" && "❌"}
                      {" " + submission.status.toUpperCase()}
                    </span>
                  </div>

                  <p className="submission-description">{submission.description}</p>

                  <div className="submission-meta">
                    <span>📝 {submission.category}</span>
                    <span>👤 {submission.author_name}</span>
                    <span>📅 {formatDate(submission.created_at)}</span>
                    <span>⏱️ {submission.read_time}</span>
                  </div>

                  {submission.featured_image && (
                    <div className="submission-image">
                      <img src={submission.featured_image} alt={submission.title} />
                    </div>
                  )}

                  <div className="submission-content-preview">
                    <strong>Content Preview:</strong>
                    <p>{submission.content.substring(0, 200)}...</p>
                  </div>

                  {submission.review_comment && (
                    <div className="review-comment">
                      <strong>Review Comment:</strong>
                      <p>{submission.review_comment}</p>
                      {submission.reviewed_at && (
                        <small>Reviewed on {formatDate(submission.reviewed_at)}</small>
                      )}
                    </div>
                  )}

                  {submission.status === "pending" && (
                    <div className="submission-actions">
                      <button
                        className="view-btn"
                        onClick={() => setSelectedSubmission(submission)}
                      >
                        👁️ Review
                      </button>
                      <button
                        className="approve-btn"
                        disabled={processing}
                        onClick={() => handleApprove(submission.id)}
                      >
                        ✅ Approve
                      </button>
                      <button
                        className="reject-btn"
                        disabled={processing}
                        onClick={() => handleReject(submission.id)}
                      >
                        ❌ Reject
                      </button>
                    </div>
                  )}

                  {submission.status !== "pending" && (
                    <div className="submission-info">
                      {submission.status === "approved" && submission.published_at && (
                        <small>✅ Published: {formatDate(submission.published_at)}</small>
                      )}
                      <small>Views: {submission.view_count || 0}</small>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Review Modal */}
        {selectedSubmission && (
          <div className="review-modal-overlay" onClick={() => setSelectedSubmission(null)}>
            <div className="review-modal" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Review Submission</h2>
                <button className="close-btn" onClick={() => setSelectedSubmission(null)}>
                  ✕
                </button>
              </div>

              <div className="modal-content">
                <h3>{selectedSubmission.title}</h3>
                <div className="modal-meta">
                  <span>📝 {selectedSubmission.category}</span>
                  <span>👤 {selectedSubmission.author_name}</span>
                  <span>📧 {selectedSubmission.author_email}</span>
                </div>

                <div className="modal-description">
                  <strong>Description:</strong>
                  <p>{selectedSubmission.description}</p>
                </div>

                {selectedSubmission.featured_image && (
                  <div className="modal-image">
                    <img src={selectedSubmission.featured_image} alt={selectedSubmission.title} />
                  </div>
                )}

                <div className="modal-full-content">
                  <strong>Full Article:</strong>
                  <div className="content-text">{selectedSubmission.content}</div>
                </div>

                <div className="review-form">
                  <label>Review Comment:</label>
                  <textarea
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                    placeholder="Add your review comments here (required for rejection)..."
                    rows="4"
                  />
                </div>

                <div className="modal-actions">
                  <button
                    className="approve-btn"
                    onClick={() => handleApprove(selectedSubmission.id)}
                    disabled={processing}
                  >
                    ✅ Approve
                  </button>
                  <button
                    className="reject-btn"
                    onClick={() => handleReject(selectedSubmission.id)}
                    disabled={processing || !reviewComment.trim()}
                  >
                    ❌ Reject
                  </button>
                  <button
                    className="cancel-btn"
                    onClick={() => setSelectedSubmission(null)}
                    disabled={processing}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      <Footer />
    </>
  );
}
