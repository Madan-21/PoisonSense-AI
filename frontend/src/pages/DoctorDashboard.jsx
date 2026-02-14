import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/DoctorDashboard.css";

export default function DoctorDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get("/dashboard/doctor");
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching doctor dashboard:", error);
      if (error.response?.status === 403) {
        setError("Doctor privileges required");
        setTimeout(() => navigate("/dashboard"), 2000);
      } else {
        setError("Failed to load dashboard");
      }
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="doctor-dashboard">
          <div className="loading-spinner">Loading dashboard...</div>
        </div>
        <Footer />
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="doctor-dashboard">
          <div className="error-message">{error}</div>
        </div>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="doctor-dashboard">
        <div className="dashboard-header">
          <div className="header-content">
            <h1>🩺 Doctor Dashboard</h1>
            <p className="subtitle">Welcome, Dr. {stats?.doctor_info?.name || "Doctor"}</p>
          </div>
          {stats?.doctor_info?.verification_status === "verified" && (
            <div className="verified-badge">
              <span className="badge-icon">✓</span>
              Verified Medical Professional
            </div>
          )}
        </div>

        {/* Doctor Info Card */}
        <div className="info-card">
          <h3>Professional Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="label">Specialization:</span>
              <span className="value">{stats?.doctor_info?.specialization || "Not specified"}</span>
            </div>
            <div className="info-item">
              <span className="label">Registration:</span>
              <span className="value">{stats?.doctor_info?.registration || "Not provided"}</span>
            </div>
            <div className="info-item">
              <span className="label">Verification Status:</span>
              <span className={`status ${stats?.doctor_info?.verification_status}`}>
                {stats?.doctor_info?.verification_status || "Pending"}
              </span>
            </div>
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="stats-grid">
          <div className="stat-card blog-stats">
            <div className="stat-icon">📝</div>
            <div className="stat-info">
              <h3>{stats?.blog_stats?.total || 0}</h3>
              <p>Total Articles</p>
            </div>
          </div>
          <div className="stat-card pending-stats">
            <div className="stat-icon">⏳</div>
            <div className="stat-info">
              <h3>{stats?.blog_stats?.pending || 0}</h3>
              <p>Pending Review</p>
            </div>
          </div>
          <div className="stat-card approved-stats">
            <div className="stat-icon">✅</div>
            <div className="stat-info">
              <h3>{stats?.blog_stats?.approved || 0}</h3>
              <p>Published Articles</p>
            </div>
          </div>
          <div className="stat-card case-stats">
            <div className="stat-icon">🏥</div>
            <div className="stat-info">
              <h3>{stats?.case_stats?.total_consultations || 0}</h3>
              <p>Case Consultations</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="action-grid">
            <button className="action-btn primary" onClick={() => navigate("/submit-article")}>
              <span className="btn-icon">✍️</span>
              Write Medical Article
            </button>
            <button className="action-btn secondary" onClick={() => navigate("/blog")}>
              <span className="btn-icon">📚</span>
              View Community Blog
            </button>
            <button className="action-btn secondary" onClick={() => navigate("/poison-management")}>
              <span className="btn-icon">💊</span>
              Antidote Database
            </button>
            <button className="action-btn secondary" onClick={() => navigate("/ai-assistant")}>
              <span className="btn-icon">🤖</span>
              AI Assistant
            </button>
          </div>
        </div>

        {/* Recent Cases */}
        {stats?.case_stats?.recent_cases && stats.case_stats.recent_cases.length > 0 && (
          <div className="recent-section">
            <h2>Recent Case Consultations</h2>
            <div className="cases-list">
              {stats.case_stats.recent_cases.map((case_item) => (
                <div key={case_item.id} className="case-card">
                  <div className="case-header">
                    <span className="case-id">Case #{case_item.id}</span>
                    <span className={`severity-badge ${case_item.severity}`}>
                      {case_item.severity || "Unknown"}
                    </span>
                  </div>
                  <div className="case-body">
                    <p className="poison-name">
                      <strong>Poison:</strong> {case_item.predicted_poison || "Unknown"}
                    </p>
                    <p className="case-date">
                      <strong>Date:</strong> {new Date(case_item.date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Benefits Banner */}
        <div className="benefits-banner">
          <h3>👨‍⚕️ Doctor Benefits</h3>
          <ul>
            <li>✅ Your medical articles are auto-approved (no waiting for review)</li>
            <li>✅ Verified Doctor badge on all your posts and comments</li>
            <li>✅ Access to advanced medical resources and case studies</li>
            <li>✅ Priority visibility in the medical community</li>
          </ul>
        </div>
      </div>
      <Footer />
    </>
  );
}
