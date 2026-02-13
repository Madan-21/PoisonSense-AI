import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/HospitalDashboard.css";
import "../styles/HospitalPages.css";

export default function HospitalInventory() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [inventory, setInventory] = useState({
    antidotes_available: [],
    toxicology_tests: [],
    facilities: [],
  });

  const [newAntidote, setNewAntidote] = useState("");
  const [newFacility, setNewFacility] = useState("");
  const [newTest, setNewTest] = useState({ name: "", price: "", duration: "" });

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      const res = await api.get("/hospitals/my-hospital/inventory");
      setInventory({
        antidotes_available: res.data.antidotes_available || [],
        toxicology_tests: res.data.toxicology_tests || [],
        facilities: res.data.facilities || [],
      });
    } catch (err) {
      if (err.response?.status === 403) {
        setError("Hospital admin privileges required");
        setTimeout(() => navigate("/dashboard"), 2000);
      } else if (err.response?.status === 404) {
        setError("No hospital associated with this account");
      } else {
        setError("Failed to load inventory");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError("");
    try {
      await api.put("/hospitals/my-hospital/inventory", {
        antidotes: inventory.antidotes_available,
        toxicology_tests: inventory.toxicology_tests,
        facilities: inventory.facilities,
      });
      setSuccess("✅ Inventory updated successfully!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError("Failed to save inventory changes");
    } finally {
      setSaving(false);
    }
  };

  const addAntidote = () => {
    const name = newAntidote.trim();
    if (!name) return;
    if (inventory.antidotes_available.includes(name)) return;
    setInventory((p) => ({ ...p, antidotes_available: [...p.antidotes_available, name] }));
    setNewAntidote("");
  };

  const removeAntidote = (idx) => {
    setInventory((p) => ({
      ...p,
      antidotes_available: p.antidotes_available.filter((_, i) => i !== idx),
    }));
  };

  const addFacility = () => {
    const name = newFacility.trim();
    if (!name) return;
    if (inventory.facilities.includes(name)) return;
    setInventory((p) => ({ ...p, facilities: [...p.facilities, name] }));
    setNewFacility("");
  };

  const removeFacility = (idx) => {
    setInventory((p) => ({
      ...p,
      facilities: p.facilities.filter((_, i) => i !== idx),
    }));
  };

  const addTest = () => {
    if (!newTest.name.trim()) return;
    const testObj = {
      name: newTest.name.trim(),
      price: newTest.price.trim() || null,
      duration: newTest.duration.trim() || null,
    };
    setInventory((p) => ({ ...p, toxicology_tests: [...p.toxicology_tests, testObj] }));
    setNewTest({ name: "", price: "", duration: "" });
  };

  const removeTest = (idx) => {
    setInventory((p) => ({
      ...p,
      toxicology_tests: p.toxicology_tests.filter((_, i) => i !== idx),
    }));
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="hospital-dashboard">
          <div className="loading-spinner">Loading inventory...</div>
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
            <h1>📦 Manage Inventory</h1>
            <p className="subtitle">Add, remove, and update hospital supplies</p>
          </div>
          <button className="back-btn" onClick={() => navigate("/hospital/dashboard")}>
            ← Back to Dashboard
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {/* Antidotes Section */}
        <div className="inventory-section">
          <div className="section-header">
            <h2>💊 Antidotes in Stock</h2>
            <span className="count-badge">{inventory.antidotes_available.length} items</span>
          </div>
          <div className="inventory-items">
            {inventory.antidotes_available.map((antidote, idx) => (
              <div key={idx} className="inventory-chip">
                <span className="chip-icon">💊</span>
                <span className="chip-text">{antidote}</span>
                <button className="chip-remove" onClick={() => removeAntidote(idx)} title="Remove">
                  ✕
                </button>
              </div>
            ))}
            {inventory.antidotes_available.length === 0 && (
              <p className="empty-hint">No antidotes listed. Add some below.</p>
            )}
          </div>
          <div className="add-row">
            <input
              type="text"
              value={newAntidote}
              onChange={(e) => setNewAntidote(e.target.value)}
              placeholder="e.g. Atropine, Naloxone, Activated Charcoal..."
              onKeyDown={(e) => e.key === "Enter" && addAntidote()}
            />
            <button className="add-btn" onClick={addAntidote}>+ Add</button>
          </div>
        </div>

        {/* Facilities Section */}
        <div className="inventory-section">
          <div className="section-header">
            <h2>🏢 Facilities</h2>
            <span className="count-badge">{inventory.facilities.length} items</span>
          </div>
          <div className="inventory-items">
            {inventory.facilities.map((facility, idx) => (
              <div key={idx} className="inventory-chip facility-chip">
                <span className="chip-icon">✓</span>
                <span className="chip-text">{facility}</span>
                <button className="chip-remove" onClick={() => removeFacility(idx)} title="Remove">
                  ✕
                </button>
              </div>
            ))}
            {inventory.facilities.length === 0 && (
              <p className="empty-hint">No facilities listed. Add some below.</p>
            )}
          </div>
          <div className="add-row">
            <input
              type="text"
              value={newFacility}
              onChange={(e) => setNewFacility(e.target.value)}
              placeholder="e.g. ICU, Emergency Ward, Toxicology Lab..."
              onKeyDown={(e) => e.key === "Enter" && addFacility()}
            />
            <button className="add-btn" onClick={addFacility}>+ Add</button>
          </div>
        </div>

        {/* Toxicology Tests Section */}
        <div className="inventory-section">
          <div className="section-header">
            <h2>🔬 Toxicology Tests</h2>
            <span className="count-badge">{inventory.toxicology_tests.length} tests</span>
          </div>
          <div className="tests-table-wrap">
            {inventory.toxicology_tests.length > 0 ? (
              <table className="tests-manage-table">
                <thead>
                  <tr>
                    <th>Test Name</th>
                    <th>Price</th>
                    <th>Duration</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {inventory.toxicology_tests.map((test, idx) => {
                    const t = typeof test === "object" ? test : { name: test };
                    return (
                      <tr key={idx}>
                        <td>🔬 {t.name}</td>
                        <td>{t.price || "—"}</td>
                        <td>{t.duration || "—"}</td>
                        <td>
                          <button className="remove-row-btn" onClick={() => removeTest(idx)}>
                            ✕
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            ) : (
              <p className="empty-hint">No toxicology tests listed yet.</p>
            )}
          </div>
          <div className="add-row test-add-row">
            <input
              type="text"
              value={newTest.name}
              onChange={(e) => setNewTest({ ...newTest, name: e.target.value })}
              placeholder="Test name *"
              className="test-name-input"
            />
            <input
              type="text"
              value={newTest.price}
              onChange={(e) => setNewTest({ ...newTest, price: e.target.value })}
              placeholder="Price (e.g. NPR 2,500)"
              className="test-price-input"
            />
            <input
              type="text"
              value={newTest.duration}
              onChange={(e) => setNewTest({ ...newTest, duration: e.target.value })}
              placeholder="Duration (e.g. 2-4 hours)"
              className="test-duration-input"
            />
            <button className="add-btn" onClick={addTest}>+ Add</button>
          </div>
        </div>

        {/* Save Button */}
        <div className="save-bar">
          <button className="save-btn" onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "💾 Save All Changes"}
          </button>
        </div>
      </div>
      <Footer />
    </>
  );
}
