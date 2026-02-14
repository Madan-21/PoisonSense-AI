import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/HospitalDashboard.css";

export default function HospitalDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get("/dashboard/hospital");
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching hospital dashboard:", error);
      if (error.response?.status === 403) {
        setError("Hospital admin privileges required");
        setTimeout(() => navigate("/dashboard"), 2000);
      } else if (error.response?.status === 404) {
        setError("No hospital associated with this account");
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
        <div className="hospital-dashboard">
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
        <div className="hospital-dashboard">
          <div className="error-message">{error}</div>
        </div>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="hospital-dashboard">
        <div className="dashboard-header">
          <div className="header-content">
            <h1>🏥 Hospital Dashboard</h1>
            <p className="subtitle">{stats?.hospital_info?.name || "Hospital Management Portal"}</p>
          </div>
          {stats?.hospital_info?.is_24_hours && (
            <div className="available-badge">
              <span className="badge-icon">🕐</span>
              24/7 Available
            </div>
          )}
        </div>

        {/* Hospital Info Card */}
        <div className="info-card">
          <h3>Hospital Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="label">Type:</span>
              <span className="value">{typeof stats?.hospital_info?.type === 'object' ? stats?.hospital_info?.type?.value || JSON.stringify(stats?.hospital_info?.type) : (stats?.hospital_info?.type || "Not specified")}</span>
            </div>
            <div className="info-item">
              <span className="label">City:</span>
              <span className="value">{stats?.hospital_info?.city || "Not specified"}</span>
            </div>
            <div className="info-item">
              <span className="label">Emergency Phone:</span>
              <span className="value phone">{stats?.hospital_info?.emergency_phone || "Not provided"}</span>
            </div>
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="stats-grid">
          <div className="stat-card cases-stats">
            <div className="stat-icon">📋</div>
            <div className="stat-info">
              <h3>{stats?.case_stats?.total_cases || 0}</h3>
              <p>Total Cases</p>
            </div>
          </div>
          <div className="stat-card emergency-stats">
            <div className="stat-icon">🚨</div>
            <div className="stat-info">
              <h3>{stats?.case_stats?.emergency_cases_this_week || 0}</h3>
              <p>Emergency Cases (This Week)</p>
            </div>
          </div>
          <div className="stat-card antidotes-stats">
            <div className="stat-icon">💊</div>
            <div className="stat-info">
              <h3>{stats?.facility_info?.antidotes_available?.length || 0}</h3>
              <p>Antidotes Available</p>
            </div>
          </div>
          <div className="stat-card facility-stats">
            <div className="stat-icon">🏢</div>
            <div className="stat-info">
              <h3>{stats?.facility_info?.facilities?.length || 0}</h3>
              <p>Facilities</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="action-grid">
            <button className="action-btn primary" onClick={() => navigate("/hospital/inventory")}>
              <span className="btn-icon">📦</span>
              Manage Inventory
            </button>
            <button className="action-btn secondary" onClick={() => navigate("/hospital/update-info")}>
              <span className="btn-icon">✏️</span>
              Update Information
            </button>
            <button className="action-btn secondary" onClick={() => navigate("/hospital/reports")}>
              <span className="btn-icon">📊</span>
              View Reports
            </button>
            <button className="action-btn secondary" onClick={() => navigate("/find-help")}>
              <span className="btn-icon">🔍</span>
              Find Resources
            </button>
          </div>
        </div>

        {/* Facilities Section */}
        {stats?.facility_info?.facilities && stats.facility_info.facilities.length > 0 && (
          <div className="facilities-section">
            <h2>Available Facilities</h2>
            <div className="facilities-grid">
              {stats.facility_info.facilities.map((facility, index) => (
                <div key={index} className="facility-badge">
                  ✓ {facility}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Antidotes Section */}
        {stats?.facility_info?.antidotes_available && stats.facility_info.antidotes_available.length > 0 && (
          <div className="antidotes-section">
            <h2>Antidotes in Stock</h2>
            <div className="antidotes-list">
              {stats.facility_info.antidotes_available.map((antidote, index) => (
                <div key={index} className="antidote-card">
                  <span className="antidote-icon">💊</span>
                  <span className="antidote-name">{antidote}</span>
                  <span className="status-badge available">Available</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Cases */}
        {stats?.case_stats?.recent_cases && stats.case_stats.recent_cases.length > 0 && (
          <div className="recent-section">
            <h2>Recent Cases</h2>
            <div className="cases-table">
              <table>
                <thead>
                  <tr>
                    <th>Case ID</th>
                    <th>Poison</th>
                    <th>Severity</th>
                    <th>Antidote</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.case_stats.recent_cases.map((case_item) => (
                    <tr key={case_item.id}>
                      <td>#{case_item.id}</td>
                      <td>{case_item.predicted_poison || "Unknown"}</td>
                      <td>
                        <span className={`severity-badge ${case_item.severity}`}>
                          {case_item.severity || "Unknown"}
                        </span>
                      </td>
                      <td>{case_item.antidote || "N/A"}</td>
                      <td>{new Date(case_item.date).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Toxicology Tests */}
        {stats?.facility_info?.toxicology_tests && stats.facility_info.toxicology_tests.length > 0 && (
          <div className="tests-section">
            <h2>Available Toxicology Tests</h2>
            <div className="tests-grid">
              {stats.facility_info.toxicology_tests.map((test, index) => (
                <div key={index} className="test-badge">
                  🔬 {typeof test === "object" ? test.name : test}
                  {typeof test === "object" && test.price && (
                    <span className="test-detail"> — {test.price}</span>
                  )}
                  {typeof test === "object" && test.duration && (
                    <span className="test-detail"> ({test.duration})</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      <Footer />
    </>
  );
}
