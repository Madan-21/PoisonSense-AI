import React, { useState } from "react";
import BlogSubmissionReview from "../components/BlogSubmissionReview";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/AdminPanel.css";

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState("blog-submissions");

  return (
    <>
      <Navbar />
      <div className="admin-panel-container">
        <div className="admin-header">
          <h1>🛡️ Admin Dashboard</h1>
          <p>Manage platform content and submissions</p>
        </div>

        <div className="admin-tabs">
          <button
            className={`tab-btn ${activeTab === "blog-submissions" ? "active" : ""}`}
            onClick={() => setActiveTab("blog-submissions")}
          >
            📝 Blog Submissions
          </button>
          <button
            className={`tab-btn ${activeTab === "users" ? "active" : ""}`}
            onClick={() => setActiveTab("users")}
          >
            👥 Users
          </button>
          <button
            className={`tab-btn ${activeTab === "reports" ? "active" : ""}`}
            onClick={() => setActiveTab("reports")}
          >
            📊 Reports
          </button>
        </div>

        <div className="admin-content">
          {activeTab === "blog-submissions" && <BlogSubmissionReview />}
          {activeTab === "users" && (
            <div style={{ padding: "40px", textAlign: "center" }}>
              <h2>User Management</h2>
              <p>Coming soon...</p>
            </div>
          )}
          {activeTab === "reports" && (
            <div style={{ padding: "40px", textAlign: "center" }}>
              <h2>Reports & Analytics</h2>
              <p>Coming soon...</p>
            </div>
          )}
        </div>
      </div>
      <Footer />
    </>
  );
}

