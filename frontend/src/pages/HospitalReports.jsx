import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/HospitalDashboard.css";
import "../styles/HospitalPages.css";

export default function HospitalReports() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [period, setPeriod] = useState(30);
  const [report, setReport] = useState(null);

  useEffect(() => {
    fetchReports();
  }, [period]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/hospitals/my-hospital/reports?days=${period}`);
      setReport(res.data);
    } catch (err) {
      if (err.response?.status === 403) {
        setError("Hospital admin privileges required");
        setTimeout(() => navigate("/dashboard"), 2000);
      } else if (err.response?.status === 404) {
        setError("No hospital associated with this account");
      } else {
        setError("Failed to load reports");
      }
    } finally {
      setLoading(false);
    }
  };

  const severityColor = (sev) => {
    const map = {
      mild: "#16a34a",
      moderate: "#d97706",
      severe: "#dc2626",
      critical: "#7c3aed",
    };
    return map[sev] || "#6b7280";
  };

  if (loading && !report) {
    return (
      <>
        <Navbar />
        <div className="hospital-dashboard">
          <div className="loading-spinner">Loading reports...</div>
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
            <h1>📊 Hospital Reports</h1>
            <p className="subtitle">{report?.hospital_name || "Hospital"} — Case Analytics</p>
          </div>
          <button className="back-btn" onClick={() => navigate("/hospital/dashboard")}>
            ← Back to Dashboard
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {/* Period Selector */}
        <div className="period-selector">
          {[7, 30, 90, 365].map((d) => (
            <button
              key={d}
              className={`period-btn ${period === d ? "active" : ""}`}
              onClick={() => setPeriod(d)}
            >
              {d === 7 ? "7 Days" : d === 30 ? "30 Days" : d === 90 ? "3 Months" : "1 Year"}
            </button>
          ))}
        </div>

        {report && (
          <>
            {/* Summary Cards */}
            <div className="stats-grid">
              <div className="stat-card cases-stats">
                <div className="stat-icon">📋</div>
                <div className="stat-info">
                  <h3>{report.total_cases_all_time}</h3>
                  <p>Total Cases (All Time)</p>
                </div>
              </div>
              <div className="stat-card emergency-stats">
                <div className="stat-icon">📈</div>
                <div className="stat-info">
                  <h3>{report.cases_in_period}</h3>
                  <p>Cases in Last {period} Days</p>
                </div>
              </div>
              <div className="stat-card antidotes-stats">
                <div className="stat-icon">🧪</div>
                <div className="stat-info">
                  <h3>{report.top_poisons?.length || 0}</h3>
                  <p>Distinct Poisons</p>
                </div>
              </div>
              <div className="stat-card facility-stats">
                <div className="stat-icon">⚠️</div>
                <div className="stat-info">
                  <h3>{(report.severity_breakdown?.severe || 0) + (report.severity_breakdown?.critical || 0)}</h3>
                  <p>Severe / Critical</p>
                </div>
              </div>
            </div>

            {/* Severity Breakdown */}
            <div className="report-section">
              <h2>📊 Severity Breakdown</h2>
              {Object.keys(report.severity_breakdown || {}).length > 0 ? (
                <div className="severity-bars">
                  {Object.entries(report.severity_breakdown).map(([sev, count]) => {
                    const maxCount = Math.max(...Object.values(report.severity_breakdown));
                    const pct = maxCount > 0 ? (count / maxCount) * 100 : 0;
                    return (
                      <div key={sev} className="severity-bar-row">
                        <span className="bar-label">
                          <span className={`severity-badge ${sev}`}>{sev}</span>
                        </span>
                        <div className="bar-track">
                          <div
                            className="bar-fill"
                            style={{ width: `${pct}%`, backgroundColor: severityColor(sev) }}
                          />
                        </div>
                        <span className="bar-count">{count}</span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="empty-hint">No severity data available for this period.</p>
              )}
            </div>

            {/* Top Poisons */}
            <div className="report-section">
              <h2>🧪 Top Poisons Encountered</h2>
              {report.top_poisons?.length > 0 ? (
                <div className="poison-list">
                  {report.top_poisons.map((p, idx) => (
                    <div key={idx} className="poison-row">
                      <span className="poison-rank">#{idx + 1}</span>
                      <span className="poison-name">{p.name}</span>
                      <span className="poison-count">{p.count} case{p.count !== 1 ? "s" : ""}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="empty-hint">No poison data available for this period.</p>
              )}
            </div>

            {/* Recent Cases Table */}
            <div className="report-section">
              <h2>📋 Recent Cases</h2>
              {report.recent_cases?.length > 0 ? (
                <div className="cases-table">
                  <table>
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Poison</th>
                        <th>Severity</th>
                        <th>Antidote Suggested</th>
                        <th>Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.recent_cases.map((c) => (
                        <tr key={c.id}>
                          <td>#{c.id}</td>
                          <td>{c.predicted_poison || "Unknown"}</td>
                          <td>
                            <span className={`severity-badge ${c.severity}`}>
                              {c.severity || "Unknown"}
                            </span>
                          </td>
                          <td>{c.antidote || "N/A"}</td>
                          <td>{new Date(c.date).toLocaleDateString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="empty-hint">No case data for this period.</p>
              )}
            </div>
          </>
        )}
      </div>
      <Footer />
    </>
  );
}
