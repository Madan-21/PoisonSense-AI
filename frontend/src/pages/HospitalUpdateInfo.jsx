import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/HospitalDashboard.css";
import "../styles/HospitalPages.css";

export default function HospitalUpdateInfo() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    emergency_phone: "",
    email: "",
    website: "",
    address: "",
    city: "",
    state: "",
    is_24_hours: false,
    operating_hours: "",
  });

  useEffect(() => {
    fetchHospitalInfo();
  }, []);

  const fetchHospitalInfo = async () => {
    try {
      const res = await api.get("/hospitals/my-hospital");
      const h = res.data;
      setFormData({
        name: h.name || "",
        phone: h.phone || "",
        emergency_phone: h.emergency_phone || "",
        email: h.email || "",
        website: h.website || "",
        address: h.address || "",
        city: h.city || "",
        state: h.state || "",
        is_24_hours: h.is_24_hours || false,
        operating_hours: h.operating_hours || "",
      });
    } catch (err) {
      if (err.response?.status === 403) {
        setError("Hospital admin privileges required");
        setTimeout(() => navigate("/dashboard"), 2000);
      } else if (err.response?.status === 404) {
        setError("No hospital associated with this account");
      } else {
        setError("Failed to load hospital information");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((p) => ({ ...p, [name]: type === "checkbox" ? checked : value }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError("");
    try {
      // Only send fields that have a non-empty value
      const payload = {};
      Object.entries(formData).forEach(([key, val]) => {
        if (typeof val === "boolean") {
          payload[key] = val;
        } else if (typeof val === "string" && val.trim()) {
          payload[key] = val.trim();
        }
      });

      await api.put("/hospitals/my-hospital", payload);
      setSuccess("✅ Hospital information updated successfully!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update hospital information");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="hospital-dashboard">
          <div className="loading-spinner">Loading hospital information...</div>
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
            <h1>✏️ Update Information</h1>
            <p className="subtitle">Manage your hospital's profile and contact details</p>
          </div>
          <button className="back-btn" onClick={() => navigate("/hospital/dashboard")}>
            ← Back to Dashboard
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {/* Basic Info */}
        <div className="form-section">
          <h2>🏥 Basic Information</h2>
          <div className="form-grid">
            <div className="form-field">
              <label>Hospital Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Hospital name"
              />
            </div>
            <div className="form-field">
              <label>City</label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleChange}
                placeholder="City"
              />
            </div>
            <div className="form-field">
              <label>State / Province</label>
              <input
                type="text"
                name="state"
                value={formData.state}
                onChange={handleChange}
                placeholder="State / Province"
              />
            </div>
            <div className="form-field full-width">
              <label>Address</label>
              <textarea
                name="address"
                value={formData.address}
                onChange={handleChange}
                placeholder="Full address"
                rows={2}
              />
            </div>
          </div>
        </div>

        {/* Contact */}
        <div className="form-section">
          <h2>📞 Contact Details</h2>
          <div className="form-grid">
            <div className="form-field">
              <label>Phone</label>
              <input
                type="text"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+977-..."
              />
            </div>
            <div className="form-field">
              <label>Emergency Phone</label>
              <input
                type="text"
                name="emergency_phone"
                value={formData.emergency_phone}
                onChange={handleChange}
                placeholder="Emergency contact number"
              />
            </div>
            <div className="form-field">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="hospital@example.com"
              />
            </div>
            <div className="form-field">
              <label>Website</label>
              <input
                type="text"
                name="website"
                value={formData.website}
                onChange={handleChange}
                placeholder="https://..."
              />
            </div>
          </div>
        </div>

        {/* Operating Hours */}
        <div className="form-section">
          <h2>🕐 Operating Hours</h2>
          <div className="form-grid">
            <div className="form-field">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  name="is_24_hours"
                  checked={formData.is_24_hours}
                  onChange={handleChange}
                />
                <span>Open 24 Hours</span>
              </label>
            </div>
            {!formData.is_24_hours && (
              <div className="form-field full-width">
                <label>Operating Hours</label>
                <input
                  type="text"
                  name="operating_hours"
                  value={formData.operating_hours}
                  onChange={handleChange}
                  placeholder="e.g. Mon-Fri 8AM-8PM, Sat-Sun 10AM-4PM"
                />
              </div>
            )}
          </div>
        </div>

        {/* Save */}
        <div className="save-bar">
          <button className="save-btn" onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "💾 Save Changes"}
          </button>
        </div>
      </div>
      <Footer />
    </>
  );
}
