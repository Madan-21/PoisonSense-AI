import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { useAuth } from "../context/AuthContext";
import { userApi } from "../api/userApi";
import { getErrorMessage } from "../utils/errorHandler";
import "../styles/Profile.css";

const Profile = () => {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem("poisonsense_settings");
    if (saved) {
      try { return JSON.parse(saved).theme || "light"; } catch { /* ignore */ }
    }
    return "light";
  });
  const [language, setLanguage] = useState(() => localStorage.getItem("poisonsense_language") || "English");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const { user, logout, refreshUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem("poisonsense_settings");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return {
          pushNotifications: parsed.pushNotifications ?? true,
          locationServices: parsed.locationServices ?? true,
          emergencyAlerts: parsed.emergencyAlerts ?? true,
        };
      } catch { /* ignore */ }
    }
    return { pushNotifications: true, locationServices: true, emergencyAlerts: true };
  });

  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    phoneNumber: "",
    dateOfBirth: "",
    bloodType: "",
    allergies: "",
    medicalConditions: "",
  });

  const [emergencyContacts, setEmergencyContacts] = useState([]);
  const [showAddContactModal, setShowAddContactModal] = useState(false);
  const [newContact, setNewContact] = useState({
    name: "",
    relationship: "",
    phone: "",
    isPrimary: false,
  });

  // Load profile
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setIsLoading(true);

        const profile = await userApi.getProfile();
        setFormData({
          fullName: profile.full_name || "",
          email: profile.email || "",
          phoneNumber: profile.phone || "",
          dateOfBirth: profile.date_of_birth ? profile.date_of_birth.split("T")[0] : "",
          bloodType: profile.blood_group || "",
          allergies: profile.allergies || "",
          medicalConditions: profile.medical_conditions || "",
        });

        const contacts = await userApi.getEmergencyContacts();
        setEmergencyContacts(
          contacts.map((c) => ({
            id: c.id,
            name: c.name,
            relationship: c.relation_type || c.relationship,
            phone: c.phone,
            isPrimary: c.is_primary,
          }))
        );
      } catch (err) {
        setError("Failed to load profile. Please try again.");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    if (!authLoading && !user) {
      navigate("/login");
      return;
    }
    if (user) fetchProfile();
  }, [user, navigate, authLoading]);

  // Theme apply
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const initials = useMemo(() => {
    const name = (formData.fullName || "User").trim();
    const parts = name.split(" ").filter(Boolean);
    if (parts.length === 1) return parts[0][0]?.toUpperCase() || "U";
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }, [formData.fullName]);

  const completeness = useMemo(() => {
    const fields = [
      formData.fullName,
      formData.email,
      formData.phoneNumber,
      formData.dateOfBirth,
      formData.bloodType,
      formData.allergies,
      formData.medicalConditions,
    ];
    const filled = fields.filter((x) => String(x || "").trim().length > 0).length;
    return Math.round((filled / fields.length) * 100);
  }, [formData]);

  const conditionsCount = useMemo(() => {
    const text = (formData.medicalConditions || "").trim();
    if (!text) return 0;
    // rough count by comma or new line
    return text.split(/,|\n/).map(s => s.trim()).filter(Boolean).length;
  }, [formData.medicalConditions]);

  const allergyCount = useMemo(() => {
    const text = (formData.allergies || "").trim();
    if (!text) return 0;
    return text.split(/,|\n/).map(s => s.trim()).filter(Boolean).length;
  }, [formData.allergies]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const handleSettingChange = async (setting) => {
    const newValue = !settings[setting];

    // Handle push notification permission
    if (setting === "pushNotifications" && newValue) {
      if (!("Notification" in window)) {
        setError("Push notifications are not supported in this browser.");
        setTimeout(() => setError(null), 3000);
        return;
      }
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        setError("Notification permission denied. Please enable it in browser settings.");
        setTimeout(() => setError(null), 3000);
        return;
      }
      new Notification("🧪 PoisonSense AI", {
        body: "Push notifications are now enabled! You'll receive updates and alerts.",
        icon: "/images/logo.png",
      });
    }

    // Handle emergency alerts enable
    if (setting === "emergencyAlerts" && newValue) {
      if (!("Notification" in window)) {
        setError("Emergency alerts require notification support in your browser.");
        setTimeout(() => setError(null), 3000);
        return;
      }
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        setError("Notification permission is required for emergency alerts.");
        setTimeout(() => setError(null), 3000);
        return;
      }
      new Notification("🚨 Emergency Alerts Enabled", {
        body: "You'll now receive critical poison emergency notifications.",
        icon: "/images/logo.png",
        requireInteraction: true,
      });
    }

    setSettings((p) => {
      const updated = { ...p, [setting]: newValue };
      // Auto-persist to localStorage on every change
      localStorage.setItem("poisonsense_settings", JSON.stringify({
        ...updated,
        theme,
        language,
      }));
      return updated;
    });

    const labels = {
      pushNotifications: newValue ? "✅ Push notifications enabled" : "🔕 Push notifications disabled",
      emergencyAlerts: newValue ? "🚨 Emergency alerts enabled" : "🔕 Emergency alerts disabled",
      locationServices: newValue ? "📍 Location services enabled" : "📍 Location services disabled",
    };
    setSuccessMessage(labels[setting] || "✅ Setting updated!");
    setTimeout(() => setSuccessMessage(null), 2500);
  };

  const handleSaveSettings = () => {
    setError(null);
    // Persist all settings to localStorage
    localStorage.setItem("poisonsense_settings", JSON.stringify({
      ...settings,
      theme,
      language,
    }));
    localStorage.setItem("poisonsense_language", language);
    setSuccessMessage("✅ All settings saved successfully!");
    setTimeout(() => setSuccessMessage(null), 2500);
  };

  const handleSaveChanges = async () => {
    setError(null);
    setSuccessMessage(null);
    setIsSaving(true);

    try {
      const updateData = {
        full_name: formData.fullName,
        phone: formData.phoneNumber,
      };

      if (formData.dateOfBirth) {
        const isoDate = formData.dateOfBirth;
        updateData.date_of_birth = `${isoDate}T00:00:00`;
      }
      if (formData.bloodType) updateData.blood_group = formData.bloodType;
      if (formData.allergies) updateData.allergies = formData.allergies;
      if (formData.medicalConditions) updateData.medical_conditions = formData.medicalConditions;

      await userApi.updateProfile(updateData);
      
      // Refresh user data in AuthContext to update navbar
      await refreshUser();

      setSuccessMessage("✅ Profile updated successfully!");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      const msg = getErrorMessage(err, "Failed to save changes");
      setError(`❌ ${msg}`);
      setTimeout(() => setError(null), 4500);
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddContact = async () => {
    if (!newContact.name || !newContact.phone || !newContact.relationship) {
      setError("Please fill in all contact fields");
      setTimeout(() => setError(null), 2500);
      return;
    }

    setIsSaving(true);
    try {
      const payload = {
        name: newContact.name,
        phone: newContact.phone,
        relationship: newContact.relationship,
        is_primary: newContact.isPrimary,
      };

      const added = await userApi.addEmergencyContact(payload);

      setEmergencyContacts((prev) => [
        ...prev,
        {
          id: added.id,
          name: added.name,
          relationship: added.relation_type || added.relationship,
          phone: added.phone,
          isPrimary: added.is_primary,
        },
      ]);

      setNewContact({ name: "", relationship: "", phone: "", isPrimary: false });
      setShowAddContactModal(false);

      setSuccessMessage("✅ Emergency contact added!");
      setTimeout(() => setSuccessMessage(null), 2500);
    } catch (err) {
      const msg = getErrorMessage(err, "Failed to add contact");
      setError(`❌ ${msg}`);
      setTimeout(() => setError(null), 3500);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteContact = async (id) => {
    if (!window.confirm("Delete this emergency contact?")) return;
    try {
      await userApi.deleteEmergencyContact(id);
      setEmergencyContacts((p) => p.filter((c) => c.id !== id));
      setSuccessMessage("✅ Contact deleted!");
      setTimeout(() => setSuccessMessage(null), 2500);
    } catch (err) {
      const msg = getErrorMessage(err, "Failed to delete contact");
      setError(`❌ ${msg}`);
      setTimeout(() => setError(null), 3500);
    }
  };

  const handleTogglePrimary = async (contact) => {
    try {
      const payload = {
        name: contact.name,
        phone: contact.phone,
        relationship: contact.relationship,
        is_primary: !contact.isPrimary,
      };
      await userApi.updateEmergencyContact(contact.id, payload);
      // If setting as primary, unset others; if unsetting, just update this one
      setEmergencyContacts((prev) =>
        prev.map((c) => {
          if (c.id === contact.id) return { ...c, isPrimary: !contact.isPrimary };
          if (!contact.isPrimary) return { ...c, isPrimary: false }; // new primary set, unset others
          return c;
        })
      );
      setSuccessMessage(!contact.isPrimary ? "✅ Set as primary contact!" : "✅ Removed as primary contact");
      setTimeout(() => setSuccessMessage(null), 2500);
    } catch (err) {
      const msg = getErrorMessage(err, "Failed to update contact");
      setError(`❌ ${msg}`);
      setTimeout(() => setError(null), 3500);
    }
  };

  const handleShareLocation = () => {
    if (!navigator.geolocation) {
      setError("❌ Geolocation is not supported by your browser");
      setTimeout(() => setError(null), 3000);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const primaryContact = emergencyContacts.find((c) => c.isPrimary);
        const contactName = primaryContact ? primaryContact.name : "your emergency contact";
        const mapsLink = `https://maps.google.com/?q=${latitude},${longitude}`;
        // Copy to clipboard
        navigator.clipboard.writeText(
          `Emergency! My location: ${mapsLink}`
        ).then(() => {
          setSuccessMessage(`📍 Location copied! Share it with ${contactName}. Maps link: ${mapsLink}`);
          setTimeout(() => setSuccessMessage(null), 5000);
        }).catch(() => {
          setSuccessMessage(`📍 My location: ${mapsLink}`);
          setTimeout(() => setSuccessMessage(null), 5000);
        });
      },
      (err) => {
        setError("❌ Unable to get your location. Please enable location services.");
        setTimeout(() => setError(null), 3500);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  if (authLoading) {
    return (
      <div className="profile-page">
        <Navbar />
        <main className="profile-content">
          <div className="profile-shell">
            <div className="loading-skeleton">⏳ Loading...</div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="profile-page">
        <Navbar />
        <main className="profile-content">
          <div className="profile-shell">
            <div className="loading-skeleton">⏳ Loading profile...</div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="profile-page">
      <Navbar />

      <main className="profile-content">
        <div className="profile-shell">
          {/* HERO HEADER */}
          <div className="profile-hero">
            <div className="hero-left">
              <div className="hero-avatar">
                <span>{initials}</span>
              </div>
              <div className="hero-info">
                <h1>{formData.fullName || "User Profile"}</h1>
                <p>{formData.email}</p>

                <div className="hero-meta">
                  <span className="pill">📞 {formData.phoneNumber || "No phone"}</span>
                  <span className="pill">🩸 {formData.bloodType || "Blood: N/A"}</span>
                  <span className="pill green">✅ {completeness}% Complete</span>
                </div>

                <div className="progress-wrap">
                  <div className="progress-label">
                    Profile completeness <strong>{completeness}%</strong>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${completeness}%` }} />
                  </div>
                </div>
              </div>
            </div>

            <div className="hero-actions">
              <button className="btn-primary" onClick={handleSaveChanges} disabled={isSaving}>
                {isSaving ? "Saving..." : "💾 Save Profile"}
              </button>
              <button
                className="btn-outline"
                type="button"
                onClick={() => setShowAddContactModal(true)}
              >
                + Add Emergency Contact
              </button>
              <button className="btn-danger-outline" type="button" onClick={handleLogout}>
                Log Out
              </button>
            </div>
          </div>

          {/* TOAST */}
          {(successMessage || error) && (
            <div className={`toast-modern ${error ? "err" : "ok"}`}>
              <div className="toast-icon">{error ? "⚠️" : "✅"}</div>
              <div className="toast-body">
                <strong>{error ? "Action failed" : "Success"}</strong>
                <span>{error || successMessage}</span>
              </div>
              <button
                className="toast-x"
                onClick={() => {
                  setError(null);
                  setSuccessMessage(null);
                }}
              >
                ×
              </button>
            </div>
          )}

          {/* DASHBOARD GRID */}
          <div className="profile-dashboard">
            {/* LEFT */}
            <div className="dash-left">
              {/* Health Summary Cards */}
              <div className="summary-grid">
                <div className="summary-card">
                  <div className="summary-top">
                    <span className="summary-ico">🩸</span>
                    <span className="summary-title">Blood Type</span>
                  </div>
                  <div className="summary-value">{formData.bloodType || "N/A"}</div>
                  <div className="summary-sub">Used for faster emergency help.</div>
                </div>

                <div className="summary-card">
                  <div className="summary-top">
                    <span className="summary-ico">🌿</span>
                    <span className="summary-title">Allergies</span>
                  </div>
                  <div className="summary-value">{allergyCount}</div>
                  <div className="summary-sub">Comma separated allergies.</div>
                </div>

                <div className="summary-card">
                  <div className="summary-top">
                    <span className="summary-ico">🩺</span>
                    <span className="summary-title">Conditions</span>
                  </div>
                  <div className="summary-value">{conditionsCount}</div>
                  <div className="summary-sub">Existing health conditions.</div>
                </div>
              </div>

              {/* Personal Form */}
              <section className="panel">
                <div className="panel-head">
                  <div>
                    <h2>Personal Information</h2>
                    <p>Edit your core details</p>
                  </div>
                  <span className="panel-tag">Profile</span>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Full Name</label>
                    <input
                      type="text"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleInputChange}
                      placeholder="Enter full name"
                    />
                  </div>

                  <div className="form-group">
                    <label>Email</label>
                    <input type="email" name="email" value={formData.email} disabled />
                    <small className="hint-text">Email cannot be changed</small>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Phone Number</label>
                    <input
                      type="tel"
                      name="phoneNumber"
                      value={formData.phoneNumber}
                      onChange={handleInputChange}
                      placeholder="Enter phone"
                    />
                  </div>

                  <div className="form-group">
                    <label>Date of Birth</label>
                    <input
                      type="date"
                      name="dateOfBirth"
                      value={formData.dateOfBirth}
                      onChange={handleInputChange}
                      max={new Date().toISOString().split("T")[0]}
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Blood Type</label>
                    <select name="bloodType" value={formData.bloodType} onChange={handleInputChange}>
                      <option value="">Select Blood Type</option>
                      <option value="A+">A+</option>
                      <option value="A-">A-</option>
                      <option value="B+">B+</option>
                      <option value="B-">B-</option>
                      <option value="AB+">AB+</option>
                      <option value="AB-">AB-</option>
                      <option value="O+">O+</option>
                      <option value="O-">O-</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Allergies</label>
                    <input
                      type="text"
                      name="allergies"
                      value={formData.allergies}
                      onChange={handleInputChange}
                      placeholder="e.g. peanuts, dust"
                    />
                  </div>
                </div>

                <div className="form-group full-width">
                  <label>Medical Conditions</label>
                  <textarea
                    name="medicalConditions"
                    value={formData.medicalConditions}
                    onChange={handleInputChange}
                    placeholder="e.g. asthma, diabetes"
                    rows="4"
                  />
                </div>

                <div className="panel-actions">
                  <button className="btn-primary" onClick={handleSaveChanges} disabled={isSaving}>
                    {isSaving ? "Saving..." : "Save Changes"}
                  </button>
                  <button
                    className="btn-soft"
                    type="button"
                    onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                  >
                    Back to top
                  </button>
                </div>
              </section>

              {/* Emergency Contacts */}
              <section className="panel">
                <div className="panel-head">
                  <div>
                    <h2>Emergency Contacts</h2>
                    <p>Contacts notified during emergencies</p>
                  </div>
                  <button className="btn-outline" onClick={() => setShowAddContactModal(true)}>
                    + Add Contact
                  </button>
                </div>

                {emergencyContacts.length === 0 ? (
                  <div className="empty-modern">
                    <div className="empty-badge">🆘</div>
                    <h3>No emergency contacts added</h3>
                    <p>Add at least one person so they can be alerted automatically.</p>
                    <button className="btn-primary" onClick={() => setShowAddContactModal(true)}>
                      Add First Contact
                    </button>
                  </div>
                ) : (
                  <div className="contacts-grid">
                    {emergencyContacts.map((c) => (
                      <div className={`contact-modern ${c.isPrimary ? "is-primary" : ""}`} key={c.id}>
                        <div className="contact-top">
                          <div className="contact-avatar2">
                            {c.name?.trim()?.[0]?.toUpperCase() || "C"}
                          </div>
                          <div className="contact-meta">
                            <div className="contact-name">
                              <strong>{c.name}</strong>
                              {c.isPrimary && <span className="badge-primary">★ PRIMARY</span>}
                            </div>
                            <span className="contact-rel">{c.relationship}</span>
                          </div>
                        </div>

                        <div className="contact-mid">
                          <span className="contact-chip">📞 {c.phone}</span>
                          <span className="contact-chip">⚡ Quick Alert Enabled</span>
                        </div>

                        <div className="contact-actions2">
                          <button
                            className={c.isPrimary ? "btn-primary-active" : "btn-outline"}
                            onClick={() => handleTogglePrimary(c)}
                            title={c.isPrimary ? "Remove as primary" : "Set as primary contact"}
                          >
                            {c.isPrimary ? "★ Primary" : "☆ Set Primary"}
                          </button>
                          <button className="btn-danger-outline" onClick={() => handleDeleteContact(c.id)}>
                            Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <div className="notice">
                  <div className="notice-ico">ℹ️</div>
                  <div className="notice-text">
                    <strong>Tip:</strong> Keep at least one primary contact. They will be alerted first.
                  </div>
                </div>
              </section>
            </div>

            {/* RIGHT */}
            <div className="dash-right">
              <section className="panel sticky">
                <div className="panel-head">
                  <div>
                    <h2>App Settings</h2>
                    <p>Control notifications & preferences</p>
                  </div>
                  <span className="panel-tag">System</span>
                </div>

                <div className="setting-block">
                  <div className="setting-row">
                    <div>
                      <h4>
                        Push Notifications
                        {"Notification" in window && (
                          <span className={`notif-status ${Notification.permission}`}>
                            {Notification.permission === "granted" ? "Allowed" : Notification.permission === "denied" ? "Blocked" : "Not Set"}
                          </span>
                        )}
                      </h4>
                      <p>Emergency alerts and updates</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={settings.pushNotifications}
                        onChange={() => handleSettingChange("pushNotifications")}
                      />
                      <span className="slider" />
                    </label>
                  </div>

                  <div className="setting-row">
                    <div>
                      <h4>Location Services</h4>
                      <p>Find nearby facilities quickly</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={settings.locationServices}
                        onChange={() => handleSettingChange("locationServices")}
                      />
                      <span className="slider" />
                    </label>
                  </div>

                  <div className="setting-row">
                    <div>
                      <h4>Emergency Alerts</h4>
                      <p>Critical notifications only</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={settings.emergencyAlerts}
                        onChange={() => handleSettingChange("emergencyAlerts")}
                      />
                      <span className="slider" />
                    </label>
                  </div>
                </div>

                <div className="divider" />

                <div className="setting-block">
                  <label className="setting-label">Language</label>
                  <select
                    className="language-select"
                    value={language}
                    onChange={(e) => {
                      const lang = e.target.value;
                      setLanguage(lang);
                      localStorage.setItem("poisonsense_language", lang);
                      setSuccessMessage(`🌐 Language set to ${lang}`);
                      setTimeout(() => setSuccessMessage(null), 2500);
                    }}
                  >
                    <option value="English">English</option>
                    <option value="Nepali">Nepali</option>
                    <option value="Hindi">Hindi</option>
                    <option value="Spanish">Spanish</option>
                  </select>

                  <label className="setting-label" style={{ marginTop: 14 }}>
                    Theme
                  </label>
                  <div className="theme-buttons">
                    <button
                      className={`theme-btn ${theme === "light" ? "active" : ""}`}
                      onClick={() => setTheme("light")}
                      type="button"
                    >
                      ☀️ Light
                    </button>
                    <button
                      className={`theme-btn ${theme === "dark" ? "active" : ""}`}
                      onClick={() => setTheme("dark")}
                      type="button"
                    >
                      🌙 Dark
                    </button>
                  </div>

                  <button className="btn-primary full" onClick={handleSaveSettings} type="button">
                    Save Settings
                  </button>
                </div>
              </section>

              <section className="panel">
                <div className="panel-head">
                  <div>
                    <h2>Safety Shortcut</h2>
                    <p>Quick access tools</p>
                  </div>
                  <span className="panel-tag danger">SOS</span>
                </div>

                <div className="shortcut">
                  <div className="shortcut-left">
                    <div className="shortcut-ico">📍</div>
                    <div>
                      <strong>Share Location</strong>
                      <p>Send your location to emergency contact</p>
                    </div>
                  </div>
                  <button className="btn-soft" type="button" onClick={handleShareLocation}>📍 Share</button>
                </div>

                <div className="shortcut">
                  <div className="shortcut-left">
                    <div className="shortcut-ico red">🚨</div>
                    <div>
                      <strong>Emergency Call</strong>
                      <p>Call 102 instantly</p>
                    </div>
                  </div>
                  <a className="btn-danger full-link" href="tel:102">Call 102</a>
                </div>
              </section>
            </div>
          </div>
        </div>
      </main>

      {/* Add Contact Modal */}
      {showAddContactModal && (
        <div className="modal-overlay" onClick={() => setShowAddContactModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add Emergency Contact</h3>
              <button className="modal-close" onClick={() => setShowAddContactModal(false)}>
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>Contact Name *</label>
                <input
                  type="text"
                  value={newContact.name}
                  onChange={(e) => setNewContact({ ...newContact, name: e.target.value })}
                  placeholder="Enter contact name"
                />
              </div>

              <div className="form-group">
                <label>Relationship *</label>
                <select
                  value={newContact.relationship}
                  onChange={(e) => setNewContact({ ...newContact, relationship: e.target.value })}
                >
                  <option value="">Select relationship</option>
                  <option value="Parent">Parent</option>
                  <option value="Spouse">Spouse</option>
                  <option value="Sibling">Sibling</option>
                  <option value="Child">Child</option>
                  <option value="Friend">Friend</option>
                  <option value="Guardian">Guardian</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label>Phone Number *</label>
                <input
                  type="tel"
                  value={newContact.phone}
                  onChange={(e) => setNewContact({ ...newContact, phone: e.target.value })}
                  placeholder="Enter phone number"
                />
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={newContact.isPrimary}
                    onChange={(e) => setNewContact({ ...newContact, isPrimary: e.target.checked })}
                  />
                  <span>Set as primary contact</span>
                </label>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-cancel" onClick={() => setShowAddContactModal(false)}>
                Cancel
              </button>
              <button className="btn-save" onClick={handleAddContact} disabled={isSaving}>
                {isSaving ? "Adding..." : "Add Contact"}
              </button>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
};

export default Profile;
