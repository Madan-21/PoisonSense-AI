<<<<<<< HEAD
// frontend/src/pages/Profile.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { useAuth } from "../context/AuthContext";
import { userApi } from "../api/userApi";
import "../styles/Profile.css";
=======
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';
import { userApi } from '../api/userApi';
import { getErrorMessage } from '../utils/errorHandler';
import '../styles/Profile.css';
>>>>>>> main

const Profile = () => {
  const [activeTab, setActiveTab] = useState("personal");
  const [theme, setTheme] = useState("light");
  const [language, setLanguage] = useState("English");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
<<<<<<< HEAD

  const { user, logout } = useAuth();
=======
  
  const { user, logout, loading: authLoading } = useAuth();
>>>>>>> main
  const navigate = useNavigate();

  const [settings, setSettings] = useState({
    pushNotifications: true,
    locationServices: true,
    emergencyAlerts: true,
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
    name: '',
    relationship: '',
    phone: '',
    isPrimary: false
  });

  // ✅ Add Contact
  const [showAddContact, setShowAddContact] = useState(false);
  const [newContact, setNewContact] = useState({
    name: "",
    relationship: "",
    phone: "",
    isPrimary: false,
  });

  // ✅ Edit Contact
  const [showEditContact, setShowEditContact] = useState(false);
  const [editingContactId, setEditingContactId] = useState(null);
  const [editContact, setEditContact] = useState({
    name: "",
    relationship: "",
    phone: "",
    isPrimary: false,
  });

  // Fetch profile + contacts
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setIsLoading(true);

        const profile = await userApi.getProfile();
<<<<<<< HEAD

        // ✅ FIX DOB: support ISO/YYY-MM-DD and DD/MM/YYYY
        let dob = "";
        if (profile?.date_of_birth) {
          const raw = String(profile.date_of_birth);

          if (raw.includes("-")) {
            dob = raw.split("T")[0];
          } else if (raw.includes("/")) {
            const [dd, mm, yyyy] = raw.split("/");
            dob = `${yyyy}-${String(mm).padStart(2, "0")}-${String(dd).padStart(2, "0")}`;
          }
        }

=======
        
        console.log('Profile loaded from API:', {
          dateOfBirth: profile.date_of_birth,
          formatted: profile.date_of_birth ? profile.date_of_birth.split('T')[0] : ''
        });
        
>>>>>>> main
        setFormData({
          fullName: profile?.full_name || "",
          email: profile?.email || "",
          phoneNumber: profile?.phone || "",
          dateOfBirth: dob,
          bloodType: profile?.blood_group || "",
          allergies: profile?.allergies || "",
          medicalConditions: profile?.medical_conditions || "",
        });

        const contacts = await userApi.getEmergencyContacts();
        setEmergencyContacts(
          (contacts || []).map((c) => ({
            id: c.id,
            name: c.name,
            relationship: c.relation_type || c.relationship || "",
            phone: c.phone,
            isPrimary: !!c.is_primary,
          })),
        );
      } catch (err) {
        console.error("Fetch profile error:", err);
        setError(
          err?.response?.data || err?.message || "Failed to load profile",
        );
      } finally {
        setIsLoading(false);
      }
    };
<<<<<<< HEAD

    if (user) fetchProfile();
    else navigate("/login");
  }, [user, navigate]);
=======
    
    // Only redirect if auth is not loading and there's no user
    if (!authLoading && !user) {
      navigate('/login');
      return;
    }
    
    if (user) {
      fetchProfile();
    }
  }, [user, navigate, authLoading]);
>>>>>>> main

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // ----------------- Handlers -----------------
  const handleInputChange = (e) => {
    const { name, value } = e.target;
<<<<<<< HEAD
    setFormData((prev) => ({ ...prev, [name]: value }));
=======
    
    if (name === 'dateOfBirth') {
      console.log('Date input changed:', {
        value,
        type: typeof value,
        length: value?.length
      });
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
>>>>>>> main
  };

  const handleSettingChange = (setting) => {
    setSettings((prev) => ({ ...prev, [setting]: !prev[setting] }));
  };

  const handleThemeChange = (newTheme) => setTheme(newTheme);
  const handleLanguageChange = (e) => setLanguage(e.target.value);

  const handleSaveSettings = () => {
    setSuccessMessage(
      `Settings saved!\nTheme: ${theme}\nLanguage: ${language}`,
    );
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  // ✅ Save profile
  const handleSaveChanges = async () => {
    setError(null);
    setSuccessMessage(null);
    setIsSaving(true);

    try {
      const updateData = {
        full_name: formData.fullName,
        phone: formData.phoneNumber,
        date_of_birth: formData.dateOfBirth
          ? `${formData.dateOfBirth}T00:00:00`
          : undefined,
        blood_group: formData.bloodType || undefined,
        allergies: formData.allergies || undefined,
        medical_conditions: formData.medicalConditions || undefined,
      };
<<<<<<< HEAD

      Object.keys(updateData).forEach(
        (k) => updateData[k] === undefined && delete updateData[k],
      );

      await userApi.updateProfile(updateData);

      setSuccessMessage("✅ Profile updated successfully!");
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err) {
      console.error("Profile save error:", err);

      const data = err?.response?.data;
      const msg =
        (typeof data === "string" && data) ||
        data?.detail ||
        data?.message ||
        (data && typeof data === "object" ? data : null) ||
        err?.message ||
        "Failed to save changes";

      setError(msg); // keep as object/string; UI will render safely
      setTimeout(() => setError(null), 6000);
=======
      
      // Only include optional fields if they have values
      if (formData.dateOfBirth) {
        // Backend expects full datetime, not just date
        // Convert YYYY-MM-DD to YYYY-MM-DDTHH:MM:SS format
        let dateValue = formData.dateOfBirth.trim();
        
        // Remove any extra spaces
        dateValue = dateValue.replace(/\s+/g, '');
        
        // Check different formats and convert to YYYY-MM-DD
        let isoDate;
        if (dateValue.includes('/')) {
          const parts = dateValue.split('/');
          if (parts.length === 3) {
            // Determine if it's DD/MM/YYYY or MM/DD/YYYY or YYYY/MM/DD
            if (parts[0].length === 4) {
              // YYYY/MM/DD
              isoDate = `${parts[0]}-${parts[1].padStart(2, '0')}-${parts[2].padStart(2, '0')}`;
            } else if (parts[2].length === 4) {
              // DD/MM/YYYY or MM/DD/YYYY - assume DD/MM/YYYY for international format
              isoDate = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
            }
          }
        } else if (dateValue.includes('-') && dateValue.length === 10) {
          // Already in YYYY-MM-DD format
          isoDate = dateValue;
        } else {
          // Try to parse as is
          isoDate = dateValue;
        }
        
        // Add time component to make it a valid datetime: YYYY-MM-DDTHH:MM:SS
        updateData.date_of_birth = `${isoDate}T00:00:00`;
        
        console.log('Date conversion:', {
          original: formData.dateOfBirth,
          isoDate: isoDate,
          datetime: updateData.date_of_birth
        });
      }
      if (formData.bloodType) {
        updateData.blood_group = formData.bloodType;
      }
      if (formData.allergies) {
        updateData.allergies = formData.allergies;
      }
      if (formData.medicalConditions) {
        updateData.medical_conditions = formData.medicalConditions;
      }
      
      console.log('Saving profile:', updateData);
      const result = await userApi.updateProfile(updateData);
      console.log('Profile saved successfully:', result);
      
      setSuccessMessage('✅ Profile updated successfully!');
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err) {
      console.error('Profile save error:', err);
      const errorMsg = getErrorMessage(err, 'Failed to save changes');
      setError(`❌ ${errorMsg}`);
      setTimeout(() => setError(null), 5000);
>>>>>>> main
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  // ✅ Add Contact
  const openAddContact = () => {
    setNewContact({ name: "", relationship: "", phone: "", isPrimary: false });
    setShowAddContact(true);
  };

  const closeAddContact = () => setShowAddContact(false);

  const handleNewContactChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewContact((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleAddContactSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    try {
      const payload = {
        name: newContact.name,
        relation_type: newContact.relationship,
        phone: newContact.phone,
        is_primary: newContact.isPrimary,
      };

      const created = await userApi.addEmergencyContact(payload);

      setEmergencyContacts((prev) => [
        ...prev,
        {
          id: created.id,
          name: created.name,
          relationship: created.relation_type || payload.relation_type,
          phone: created.phone || payload.phone,
          isPrimary: !!created.is_primary,
        },
      ]);

      setSuccessMessage("✅ Emergency contact added!");
      setTimeout(() => setSuccessMessage(null), 3000);
      closeAddContact();
    } catch (err) {
      console.error("Add contact error:", err);
      setError(err?.response?.data || err?.message || "Failed to add contact");
      setTimeout(() => setError(null), 6000);
    }
  };

  // ✅ Edit Contact
  const openEditContact = (contact) => {
    setEditingContactId(contact.id);
    setEditContact({
      name: contact.name || "",
      relationship: contact.relationship || "",
      phone: contact.phone || "",
      isPrimary: !!contact.isPrimary,
    });
    setShowEditContact(true);
  };

  const closeEditContact = () => {
    setShowEditContact(false);
    setEditingContactId(null);
  };

  const handleEditContactChange = (e) => {
    const { name, value, type, checked } = e.target;
    setEditContact((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleEditContactSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    try {
      const payload = {
        name: editContact.name,
        relation_type: editContact.relationship,
        phone: editContact.phone,
        is_primary: editContact.isPrimary,
      };

      const updated = await userApi.updateEmergencyContact(
        editingContactId,
        payload,
      );

      setEmergencyContacts((prev) =>
        prev.map((c) =>
          c.id === editingContactId
            ? {
                ...c,
                name: updated.name ?? payload.name,
                relationship: updated.relation_type ?? payload.relation_type,
                phone: updated.phone ?? payload.phone,
                isPrimary: updated.is_primary ?? payload.is_primary,
              }
            : c,
        ),
      );

      setSuccessMessage("✅ Contact updated!");
      setTimeout(() => setSuccessMessage(null), 3000);
      closeEditContact();
    } catch (err) {
      console.error("Update contact error:", err);
      setError(
        err?.response?.data || err?.message || "Failed to update contact",
      );
      setTimeout(() => setError(null), 6000);
    }
  };

  // ✅ Delete Contact
  const handleDeleteContact = async (id) => {
    const ok = window.confirm("Delete this contact?");
    if (!ok) return;

    setError(null);
    setSuccessMessage(null);

    try {
      await userApi.deleteEmergencyContact(id);
      setEmergencyContacts((prev) => prev.filter((c) => c.id !== id));
      setSuccessMessage("✅ Contact deleted!");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      console.error("Delete contact error:", err);
      setError(
        err?.response?.data || err?.message || "Failed to delete contact",
      );
      setTimeout(() => setError(null), 6000);
    }
  };

  const handleAddContact = async () => {
    if (!newContact.name || !newContact.phone || !newContact.relationship) {
      setError('Please fill in all contact fields');
      setTimeout(() => setError(null), 3000);
      return;
    }

    setIsSaving(true);
    try {
      const contactData = {
        name: newContact.name,
        phone: newContact.phone,
        relationship: newContact.relationship,
        is_primary: newContact.isPrimary
      };

      const addedContact = await userApi.addEmergencyContact(contactData);
      
      setEmergencyContacts([...emergencyContacts, {
        id: addedContact.id,
        name: addedContact.name,
        relationship: addedContact.relation_type,
        phone: addedContact.phone,
        isPrimary: addedContact.is_primary
      }]);

      setNewContact({ name: '', relationship: '', phone: '', isPrimary: false });
      setShowAddContactModal(false);
      setSuccessMessage('✅ Emergency contact added successfully!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      console.error('Add contact error:', err);
      const errorMsg = getErrorMessage(err, 'Failed to add contact');
      setError(`❌ ${errorMsg}. Please try again.`);
      setTimeout(() => setError(null), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteContact = async (contactId) => {
    if (!window.confirm('Are you sure you want to delete this contact?')) {
      return;
    }

    try {
      await userApi.deleteEmergencyContact(contactId);
      setEmergencyContacts(emergencyContacts.filter(c => c.id !== contactId));
      setSuccessMessage('✅ Contact deleted successfully!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      console.error('Delete contact error:', err);
      const errorMsg = getErrorMessage(err, 'Failed to delete contact');
      setError(`❌ ${errorMsg}. Please try again.`);
      setTimeout(() => setError(null), 3000);
    }
  };

  const tabs = [
    { id: "personal", label: "Personal Info" },
    { id: "emergency", label: "Emergency Contacts" },
    { id: "settings", label: "Settings" },
  ];

  // Show loading state while auth is initializing
  if (authLoading) {
    return (
      <div className="profile-page">
        <Navbar />
        <main className="profile-content">
          <div className="content-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
            <div style={{ fontSize: '18px', color: '#64748b' }}>⏳ Loading...</div>
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
        <div className="content-container">
          <div className="page-header">
            <h1>Profile & Settings</h1>
            <p>Manage your personal information and emergency contacts</p>
          </div>

          <div className="tab-navigation">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
                onClick={() => setActiveTab(tab.id)}
                type="button"
              >
                {tab.label}
              </button>
            ))}
          </div>

          {isLoading ? (
            <div style={{ padding: 20 }}>Loading...</div>
          ) : (
            <div className="tab-content">
              {/* PERSONAL */}
              {activeTab === "personal" && (
                <div className="personal-info-form">
                  <h2>Personal Information</h2>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Full Name</label>
                      <input
                        type="text"
                        name="fullName"
                        value={formData.fullName}
                        onChange={handleInputChange}
                      />
                    </div>
                    <div className="form-group">
                      <label>Email</label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        disabled
                      />
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
                      />
                    </div>
                    <div className="form-group">
                      <label>Date of Birth</label>
                      <input
                        type="date"
                        name="dateOfBirth"
                        value={formData.dateOfBirth}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Blood Type</label>
                      <select
                        name="bloodType"
                        value={formData.bloodType}
                        onChange={handleInputChange}
                      >
                        <option value="">Select</option>
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
                      />
                    </div>
                  </div>

                  <div className="form-group full-width">
                    <label>Medical Conditions</label>
                    <textarea
                      name="medicalConditions"
                      value={formData.medicalConditions}
                      onChange={handleInputChange}
                      rows="4"
                      placeholder="Enter any medical conditions"
                    />
                  </div>

<<<<<<< HEAD
                  {/* ✅ SAFE ERROR RENDERING (Your requested block) */}
                  {error && (
                    <div className="message-box error">
                      {typeof error === "string"
                        ? error
                        : JSON.stringify(error)}
                    </div>
                  )}

                  {successMessage && (
                    <div className="message-box success">{successMessage}</div>
                  )}

                  <button
                    className="save-btn"
                    onClick={handleSaveChanges}
                    disabled={isSaving}
                    type="button"
                  >
                    {isSaving ? "⏳ Saving..." : "💾 Save Changes"}
=======
                <div className="form-row">
                  <div className="form-group">
                    <label>Phone Number</label>
                    <input
                      type="tel"
                      name="phoneNumber"
                      value={formData.phoneNumber}
                      onChange={handleInputChange}
                      placeholder="Enter your phone number"
                    />
                  </div>
                  <div className="form-group">
                    <label>Date of Birth</label>
                    <input
                      type="date"
                      name="dateOfBirth"
                      value={formData.dateOfBirth}
                      onChange={handleInputChange}
                      max={new Date().toISOString().split('T')[0]}
                      placeholder="Select your date of birth"
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Blood Type</label>
                    <select
                      name="bloodType"
                      value={formData.bloodType}
                      onChange={handleInputChange}
                    >
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
                      placeholder="Enter any allergies"
                    />
                  </div>
                </div>

                <div className="form-group full-width">
                  <label>Medical Conditions</label>
                  <textarea
                    name="medicalConditions"
                    value={formData.medicalConditions}
                    onChange={handleInputChange}
                    placeholder="Enter any medical conditions"
                    rows="4"
                  ></textarea>
                </div>

                {/* Success/Error Messages */}
                {successMessage && (
                  <div className="message-box success">
                    {successMessage}
                  </div>
                )}
                {error && (
                  <div className="message-box error">
                    {error}
                  </div>
                )}

                <button 
                  className="save-btn" 
                  onClick={handleSaveChanges}
                  disabled={isSaving}
                >
                  {isSaving ? '⏳ Saving...' : '💾 Save Changes'}
                </button>
              </div>
            )}

            {activeTab === 'emergency' && (
              <div className="emergency-contacts-form">
                <div className="emergency-header">
                  <h2>Emergency Contacts</h2>
                  <button 
                    className="add-contact-btn-green"
                    onClick={() => setShowAddContactModal(true)}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                      <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                    </svg>
                    Add Contact
>>>>>>> main
                  </button>
                </div>
              )}

              {/* EMERGENCY */}
              {activeTab === "emergency" && (
                <div className="emergency-contacts-form">
                  <div className="emergency-header">
                    <h2>Emergency Contacts</h2>
                    <button
                      className="add-contact-btn-green"
                      onClick={openAddContact}
                      type="button"
                    >
                      + Add Contact
                    </button>
                  </div>

                  {/* ✅ SAFE ERROR RENDERING */}
                  {error && (
                    <div className="message-box error">
                      {typeof error === "string"
                        ? error
                        : JSON.stringify(error)}
                    </div>
                  )}
                  {successMessage && (
                    <div className="message-box success">{successMessage}</div>
                  )}

                  {emergencyContacts.map((contact) => (
                    <div key={contact.id} className="contact-card">
                      <div className="contact-left">
                        <div className="contact-info">
                          <h3>{contact.name}</h3>
                          <p>{contact.relationship}</p>
                          <span className="contact-phone">{contact.phone}</span>
                        </div>
                      </div>

                      <div className="contact-actions">
                        <button
                          className="icon-btn edit-icon"
                          type="button"
                          onClick={() => openEditContact(contact)}
                        >
                          ✏️
                        </button>
                        <button
                          className="icon-btn delete-icon"
                          type="button"
                          onClick={() => handleDeleteContact(contact.id)}
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
<<<<<<< HEAD
                  ))}

                  {/* ADD MODAL */}
                  {showAddContact && (
                    <div className="modal-backdrop">
                      <div className="modal-box">
                        <h3>Add Emergency Contact</h3>

                        <form onSubmit={handleAddContactSubmit}>
                          <input
                            type="text"
                            name="name"
                            placeholder="Full Name"
                            value={newContact.name}
                            onChange={handleNewContactChange}
                            required
                          />
                          <input
                            type="text"
                            name="relationship"
                            placeholder="Relationship"
                            value={newContact.relationship}
                            onChange={handleNewContactChange}
                            required
                          />
                          <input
                            type="text"
                            name="phone"
                            placeholder="Phone"
                            value={newContact.phone}
                            onChange={handleNewContactChange}
                            required
                          />

                          <div className="modal-actions">
                            <button
                              type="button"
                              className="btn-cancel"
                              onClick={closeAddContact}
                            >
                              Cancel
                            </button>
                            <button type="submit" className="btn-save">
                              Save
                            </button>
                          </div>
                        </form>
                      </div>
                    </div>
                  )}

                  {/* EDIT MODAL */}
                  {showEditContact && (
                    <div className="modal-backdrop">
                      <div className="modal-box">
                        <h3>Edit Emergency Contact</h3>

                        <form onSubmit={handleEditContactSubmit}>
                          <input
                            type="text"
                            name="name"
                            placeholder="Full Name"
                            value={editContact.name}
                            onChange={handleEditContactChange}
                            required
                          />
                          <input
                            type="text"
                            name="relationship"
                            placeholder="Relationship"
                            value={editContact.relationship}
                            onChange={handleEditContactChange}
                            required
                          />
                          <input
                            type="text"
                            name="phone"
                            placeholder="Phone"
                            value={editContact.phone}
                            onChange={handleEditContactChange}
                            required
                          />

                          <div className="modal-actions">
                            <button
                              type="button"
                              className="btn-cancel"
                              onClick={closeEditContact}
                            >
                              Cancel
                            </button>
                            <button type="submit" className="btn-save">
                              Update
                            </button>
                          </div>
                        </form>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* SETTINGS */}
              {activeTab === "settings" && (
                <div className="settings-form">
                  <h2>App Settings</h2>

                  <div className="setting-item">
                    <div className="setting-info">
                      <h3>Push Notifications</h3>
                      <p>Receive emergency alerts and updates</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={settings.pushNotifications}
                        onChange={() =>
                          handleSettingChange("pushNotifications")
                        }
                      />
                      <span className="slider"></span>
                    </label>
                  </div>

                  <div className="setting-item">
                    <div className="setting-info">
                      <h3>Location Services</h3>
                      <p>Find nearby emergency facilities</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={settings.locationServices}
                        onChange={() => handleSettingChange("locationServices")}
                      />
                      <span className="slider"></span>
                    </label>
                  </div>

                  <div className="setting-item">
                    <div className="setting-info">
                      <h3>Emergency Alerts</h3>
                      <p>Critical emergency notifications</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={settings.emergencyAlerts}
                        onChange={() => handleSettingChange("emergencyAlerts")}
                      />
                      <span className="slider"></span>
                    </label>
                  </div>

                  <div className="setting-group">
                    <label className="setting-label">Language</label>
                    <select
                      className="language-select"
                      value={language}
                      onChange={handleLanguageChange}
                    >
                      <option value="English">English</option>
                      <option value="Nepali">Nepali</option>
                      <option value="Hindi">Hindi</option>
                      <option value="Spanish">Spanish</option>
                    </select>
                  </div>

                  <div className="setting-group">
                    <label className="setting-label">Theme</label>
                    <div className="theme-buttons">
                      <button
                        type="button"
                        className={`theme-btn ${theme === "light" ? "active" : ""}`}
                        onClick={() => handleThemeChange("light")}
                      >
                        ☀️ Light
                      </button>

                      <button
                        type="button"
                        className={`theme-btn ${theme === "dark" ? "active" : ""}`}
                        onClick={() => handleThemeChange("dark")}
                      >
                        🌙 Dark
=======
                    <div className="contact-actions">
                      <button 
                        className="icon-btn delete-icon"
                        onClick={() => handleDeleteContact(contact.id)}
                        title="Delete contact"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="#EF4444">
                          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                        </svg>
>>>>>>> main
                      </button>
                    </div>
                  </div>

                  {successMessage && (
                    <div className="message-box success">{successMessage}</div>
                  )}

                  {/* ✅ Safe error rendering */}
                  {error && (
                    <div className="message-box error">
                      {typeof error === "string"
                        ? error
                        : JSON.stringify(error)}
                    </div>
                  )}

                  <div
                    style={{
                      display: "flex",
                      gap: "12px",
                      marginTop: "28px",
                      flexWrap: "wrap",
                    }}
                  >
                    <button
                      className="save-settings-btn"
                      onClick={handleSaveSettings}
                      type="button"
                    >
                      Save Settings
                    </button>

                    <button
                      className="log-out-btn"
                      onClick={handleLogout}
                      type="button"
                    >
                      Log Out
                    </button>
                  </div>
                </div>
<<<<<<< HEAD
              )}
            </div>
          )}
        </div>
      </main>

=======

                <button className="save-settings-btn" onClick={handleSaveSettings}>
                  Save Settings
                </button>
                <button className="log-out-btn" onClick={handleLogout}>
                  Log Out
                </button>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Add Contact Modal */}
      {showAddContactModal && (
        <div className="modal-overlay" onClick={() => setShowAddContactModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add Emergency Contact</h3>
              <button 
                className="modal-close"
                onClick={() => setShowAddContactModal(false)}
              >
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
              <button 
                className="btn-cancel"
                onClick={() => setShowAddContactModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn-save"
                onClick={handleAddContact}
                disabled={isSaving}
              >
                {isSaving ? 'Adding...' : 'Add Contact'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
>>>>>>> main
      <Footer />
    </div>
  );
};

export default Profile;

// import React, { useEffect, useState } from "react";
// import { useNavigate } from "react-router-dom";
// import Navbar from "../components/Navbar";
// import Footer from "../components/Footer";
// import { useAuth } from "../context/AuthContext";
// import { userApi } from "../api/userApi";
// import "../styles/Profile.css";

// const Profile = () => {
//   const navigate = useNavigate();
//   const { user, logout } = useAuth();

//   const [activeTab, setActiveTab] = useState("personal");
//   const [theme, setTheme] = useState("light");
//   const [language, setLanguage] = useState("English");

//   const [isLoading, setIsLoading] = useState(true);
//   const [isSaving, setIsSaving] = useState(false);

//   const [error, setError] = useState(null);
//   const [successMessage, setSuccessMessage] = useState(null);

//   const [formData, setFormData] = useState({
//     fullName: "",
//     email: "",
//     phoneNumber: "",
//     dateOfBirth: "",
//     bloodType: "",
//     allergies: "",
//     medicalConditions: "",
//   });

//   const [settings, setSettings] = useState({
//     pushNotifications: true,
//     locationServices: true,
//     emergencyAlerts: true,
//   });

//   const [emergencyContacts, setEmergencyContacts] = useState([]);

//   // -------- Add Contact Modal --------
//   const [isContactModalOpen, setIsContactModalOpen] = useState(false);
//   const [contactForm, setContactForm] = useState({
//     name: "",
//     relationship: "",
//     phone: "",
//     email: "",
//     is_primary: false,
//   });

//   // ---------- helpers ----------
//   const toBackendDOB = (yyyyMmDd) => {
//     // Backend expects datetime: "YYYY-MM-DDT00:00:00"
//     if (!yyyyMmDd) return undefined;
//     return `${yyyyMmDd}T00:00:00`;
//   };

//   const getErrorMessage = (e) => {
//     const data = e?.response?.data;

//     if (data) {
//       // FastAPI validation: {detail:[{msg:...}]}
//       if (Array.isArray(data.detail)) {
//         const first = data.detail[0];
//         return first?.msg || JSON.stringify(first);
//       }
//       if (typeof data.detail === "string") return data.detail;
//       if (typeof data.message === "string") return data.message;
//       return JSON.stringify(data);
//     }

//     if (typeof e?.message === "string") return e.message;
//     return "Something went wrong";
//   };

//   const loadProfileAndContacts = async () => {
//     setError(null);

//     const profile = await userApi.getProfile();

//     setFormData({
//       fullName: profile.full_name || "",
//       email: profile.email || "",
//       phoneNumber: profile.phone || "",
//       dateOfBirth: profile.date_of_birth ? profile.date_of_birth.split("T")[0] : "",
//       bloodType: profile.blood_group || "",
//       allergies: profile.allergies || "",
//       medicalConditions: profile.medical_conditions || "",
//     });

//     const contacts = await userApi.getEmergencyContacts();
//     setEmergencyContacts(
//       (contacts || []).map((c) => ({
//         id: c.id,
//         name: c.name,
//         relationship: c.relation_type || c.relationship || "",
//         phone: c.phone,
//         email: c.email || "",
//         isPrimary: !!c.is_primary,
//       }))
//     );
//   };

//   // ---------- mount ----------
//   useEffect(() => {
//     const run = async () => {
//       try {
//         setIsLoading(true);

//         if (!user) {
//           navigate("/login", { replace: true });
//           return;
//         }

//         await loadProfileAndContacts();
//       } catch (err) {
//         setError(getErrorMessage(err));
//       } finally {
//         setIsLoading(false);
//       }
//     };

//     run();
//     // eslint-disable-next-line react-hooks/exhaustive-deps
//   }, [user]);

//   // theme apply
//   useEffect(() => {
//     document.documentElement.setAttribute("data-theme", theme);
//   }, [theme]);

//   // ---------- form handlers ----------
//   const handleInputChange = (e) => {
//     const { name, value } = e.target;
//     setFormData((p) => ({ ...p, [name]: value }));
//   };

//   const handleSettingChange = (setting) => {
//     setSettings((p) => ({ ...p, [setting]: !p[setting] }));
//   };

//   const handleThemeChange = (newTheme) => setTheme(newTheme);

//   const handleLanguageChange = (e) => setLanguage(e.target.value);

//   const handleSaveSettings = () => {
//     setSuccessMessage(`✅ Settings saved!`);
//     setTimeout(() => setSuccessMessage(null), 2500);
//   };

//   const handleSaveChanges = async () => {
//     try {
//       setError(null);
//       setSuccessMessage(null);
//       setIsSaving(true);

//       const updateData = {
//         full_name: formData.fullName,
//         phone: formData.phoneNumber,
//       };

//       if (formData.dateOfBirth) updateData.date_of_birth = toBackendDOB(formData.dateOfBirth);
//       if (formData.bloodType) updateData.blood_group = formData.bloodType;
//       if (formData.allergies) updateData.allergies = formData.allergies;
//       if (formData.medicalConditions) updateData.medical_conditions = formData.medicalConditions;

//       await userApi.updateProfile(updateData);

//       setSuccessMessage("✅ Profile updated successfully!");
//       setTimeout(() => setSuccessMessage(null), 3000);
//     } catch (err) {
//       const msg = getErrorMessage(err);
//       setError(`❌ ${msg}`);
//       setTimeout(() => setError(null), 5000);
//     } finally {
//       setIsSaving(false);
//     }
//   };

//   // ---------- logout ----------
//   const handleLogout = async () => {
//     try {
//       await logout();
//     } catch (e) {
//       // ignore
//     } finally {
//       // go home
//       navigate("/", { replace: true });
//     }
//   };

//   // ---------- Add Contact Modal handlers ----------
//   const openAddContactModal = () => {
//     setContactForm({
//       name: "",
//       relationship: "",
//       phone: "",
//       email: "",
//       is_primary: false,
//     });
//     setIsContactModalOpen(true);
//   };

//   const closeContactModal = () => setIsContactModalOpen(false);

//   const handleContactInputChange = (e) => {
//     const { name, value, type, checked } = e.target;
//     setContactForm((prev) => ({
//       ...prev,
//       [name]: type === "checkbox" ? checked : value,
//     }));
//   };

//   const handleSaveContact = async () => {
//     try {
//       setError(null);

//       const payload = {
//         name: contactForm.name,
//         relationship: contactForm.relationship,
//         phone: contactForm.phone,
//         email: contactForm.email || null,
//         is_primary: contactForm.is_primary,
//       };

//       await userApi.addEmergencyContact(payload);

//       // reload contacts
//       const contacts = await userApi.getEmergencyContacts();
//       setEmergencyContacts(
//         (contacts || []).map((c) => ({
//           id: c.id,
//           name: c.name,
//           relationship: c.relation_type || c.relationship || "",
//           phone: c.phone,
//           email: c.email || "",
//           isPrimary: !!c.is_primary,
//         }))
//       );

//       setIsContactModalOpen(false);
//       setSuccessMessage("✅ Contact added!");
//       setTimeout(() => setSuccessMessage(null), 2500);
//     } catch (err) {
//       const msg = getErrorMessage(err);
//       setError(`❌ ${msg}`);
//       setTimeout(() => setError(null), 5000);
//     }
//   };

//   if (isLoading) {
//     return (
//       <>
//         <Navbar />
//         <div style={{ padding: 40, textAlign: "center" }}>Loading profile...</div>
//         <Footer />
//       </>
//     );
//   }

//   return (
//     <div className="profile-page">
//       <Navbar />

//       <main className="profile-content">
//         <div className="content-container">
//           <div className="page-header profile-header-row">
//             <div>
//               <h1>Profile & Settings</h1>
//               <p>Manage your personal information and emergency contacts</p>
//             </div>

//             <button className="logout-top-btn" type="button" onClick={handleLogout}>
//               Logout
//             </button>
//           </div>

//           {/* tabs */}
//           <div className="tab-navigation">
//             <button
//               className={`tab-btn ${activeTab === "personal" ? "active" : ""}`}
//               onClick={() => setActiveTab("personal")}
//               type="button"
//             >
//               Personal Info
//             </button>
//             <button
//               className={`tab-btn ${activeTab === "emergency" ? "active" : ""}`}
//               onClick={() => setActiveTab("emergency")}
//               type="button"
//             >
//               Emergency Contacts
//             </button>
//             <button
//               className={`tab-btn ${activeTab === "settings" ? "active" : ""}`}
//               onClick={() => setActiveTab("settings")}
//               type="button"
//             >
//               Settings
//             </button>
//           </div>

//           {/* messages */}
//           {successMessage && <div className="message-box success">{successMessage}</div>}
//           {error && <div className="message-box error">{error}</div>}

//           {/* PERSONAL TAB */}
//           {activeTab === "personal" && (
//             <div className="personal-info-form">
//               <h2>Personal Information</h2>

//               <div className="form-row">
//                 <div className="form-group">
//                   <label>Full Name</label>
//                   <input name="fullName" value={formData.fullName} onChange={handleInputChange} />
//                 </div>
//                 <div className="form-group">
//                   <label>Email</label>
//                   <input name="email" value={formData.email} onChange={handleInputChange} disabled />
//                 </div>
//               </div>

//               <div className="form-row">
//                 <div className="form-group">
//                   <label>Phone Number</label>
//                   <input name="phoneNumber" value={formData.phoneNumber} onChange={handleInputChange} />
//                 </div>
//                 <div className="form-group">
//                   <label>Date of Birth</label>
//                   <input type="date" name="dateOfBirth" value={formData.dateOfBirth} onChange={handleInputChange} />
//                 </div>
//               </div>

//               <div className="form-row">
//                 <div className="form-group">
//                   <label>Blood Type</label>
//                   <select name="bloodType" value={formData.bloodType} onChange={handleInputChange}>
//                     <option value="">Select</option>
//                     <option value="A+">A+</option>
//                     <option value="A-">A-</option>
//                     <option value="B+">B+</option>
//                     <option value="B-">B-</option>
//                     <option value="AB+">AB+</option>
//                     <option value="AB-">AB-</option>
//                     <option value="O+">O+</option>
//                     <option value="O-">O-</option>
//                   </select>
//                 </div>

//                 <div className="form-group">
//                   <label>Allergies</label>
//                   <input name="allergies" value={formData.allergies} onChange={handleInputChange} />
//                 </div>
//               </div>

//               <div className="form-group full-width">
//                 <label>Medical Conditions</label>
//                 <textarea
//                   name="medicalConditions"
//                   value={formData.medicalConditions}
//                   onChange={handleInputChange}
//                   rows="4"
//                 />
//               </div>

//               <button className="save-btn" type="button" onClick={handleSaveChanges} disabled={isSaving}>
//                 {isSaving ? "Saving..." : "Save Changes"}
//               </button>
//             </div>
//           )}

//           {/* EMERGENCY TAB */}
//           {activeTab === "emergency" && (
//             <div className="emergency-contacts-form">
//               <div className="emergency-header">
//                 <h2>Emergency Contacts</h2>
//                 <button
//                   type="button"
//                   className="add-contact-btn-green"
//                   onClick={openAddContactModal}
//                 >
//                   + Add Contact
//                 </button>
//               </div>

//               {emergencyContacts.length === 0 ? (
//                 <div className="empty-box">No emergency contacts yet.</div>
//               ) : (
//                 emergencyContacts.map((c) => (
//                   <div key={c.id} className="contact-card">
//                     <div className="contact-info">
//                       <h3>{c.name}</h3>
//                       <p>{c.relationship}</p>
//                       <span className="contact-phone">{c.phone}</span>
//                       {c.isPrimary && <span className="primary-badge">PRIMARY</span>}
//                     </div>
//                   </div>
//                 ))
//               )}

//               <div className="info-box">
//                 <h4>Why Emergency Contacts?</h4>
//                 <p>
//                   Emergency contacts will be notified automatically in critical situations.
//                   Keep this information up to date.
//                 </p>
//               </div>
//             </div>
//           )}

//           {/* SETTINGS TAB */}
//           {activeTab === "settings" && (
//             <div className="settings-form">
//               <h2>App Settings</h2>

//               <div className="setting-item">
//                 <div className="setting-info">
//                   <h3>Push Notifications</h3>
//                   <p>Receive emergency alerts and updates</p>
//                 </div>
//                 <input
//                   type="checkbox"
//                   checked={settings.pushNotifications}
//                   onChange={() => handleSettingChange("pushNotifications")}
//                 />
//               </div>

//               <div className="setting-item">
//                 <div className="setting-info">
//                   <h3>Location Services</h3>
//                   <p>Find nearby emergency facilities</p>
//                 </div>
//                 <input
//                   type="checkbox"
//                   checked={settings.locationServices}
//                   onChange={() => handleSettingChange("locationServices")}
//                 />
//               </div>

//               <div className="setting-item">
//                 <div className="setting-info">
//                   <h3>Emergency Alerts</h3>
//                   <p>Critical emergency notifications</p>
//                 </div>
//                 <input
//                   type="checkbox"
//                   checked={settings.emergencyAlerts}
//                   onChange={() => handleSettingChange("emergencyAlerts")}
//                 />
//               </div>

//               <div className="setting-group">
//                 <label>Language</label>
//                 <select value={language} onChange={handleLanguageChange}>
//                   <option value="English">English</option>
//                   <option value="Nepali">Nepali</option>
//                   <option value="Hindi">Hindi</option>
//                 </select>
//               </div>

//               <div className="setting-group">
//                 <label>Theme</label>
//                 <div className="theme-buttons">
//                   <button type="button" onClick={() => handleThemeChange("light")}>
//                     Light
//                   </button>
//                   <button type="button" onClick={() => handleThemeChange("dark")}>
//                     Dark
//                   </button>
//                 </div>
//               </div>

//               <button type="button" className="save-settings-btn" onClick={handleSaveSettings}>
//                 Save Settings
//               </button>
//             </div>
//           )}
//         </div>
//       </main>

//       {/* ADD CONTACT MODAL */}
//       {isContactModalOpen && (
//         <div className="modal-overlay">
//           <div className="modal-card">
//             <h3>Add Emergency Contact</h3>

//             <div className="modal-field">
//               <label>Name</label>
//               <input
//                 name="name"
//                 value={contactForm.name}
//                 onChange={handleContactInputChange}
//                 placeholder="Full name"
//               />
//             </div>

//             <div className="modal-field">
//               <label>Relationship</label>
//               <input
//                 name="relationship"
//                 value={contactForm.relationship}
//                 onChange={handleContactInputChange}
//                 placeholder="Parents / Brother / Friend"
//               />
//             </div>

//             <div className="modal-field">
//               <label>Phone</label>
//               <input
//                 name="phone"
//                 value={contactForm.phone}
//                 onChange={handleContactInputChange}
//                 placeholder="98XXXXXXXX"
//               />
//             </div>

//             <div className="modal-field">
//               <label>Email (optional)</label>
//               <input
//                 name="email"
//                 value={contactForm.email}
//                 onChange={handleContactInputChange}
//                 placeholder="example@gmail.com"
//               />
//             </div>

//             <div className="modal-field checkbox-row">
//               <input
//                 type="checkbox"
//                 name="is_primary"
//                 checked={contactForm.is_primary}
//                 onChange={handleContactInputChange}
//               />
//               <label>Make Primary</label>
//             </div>

//             <div className="modal-actions">
//               <button type="button" className="btn-cancel" onClick={closeContactModal}>
//                 Cancel
//               </button>
//               <button type="button" className="btn-save" onClick={handleSaveContact}>
//                 Save
//               </button>
//             </div>
//           </div>
//         </div>
//       )}

//       <Footer />
//     </div>
//   );
// };

// export default Profile;

// import React, { useState, useEffect } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import Navbar from '../components/Navbar';
// import Footer from '../components/Footer';
// import { useAuth } from '../context/AuthContext';
// import { userApi } from '../api/userApi';
// import '../styles/Profile.css';
// import { logoutRequest } from "../api/auth";

// const Profile = () => {
//   const [activeTab, setActiveTab] = useState('personal');
//   const [theme, setTheme] = useState('light');
//   const [language, setLanguage] = useState('English');
//   const [isLoading, setIsLoading] = useState(true);
//   const [isSaving, setIsSaving] = useState(false);
//   const [error, setError] = useState(null);
//   const [successMessage, setSuccessMessage] = useState(null);

//   const { user, logout } = useAuth();
//   const navigate = useNavigate();

//   const [settings, setSettings] = useState({
//     pushNotifications: true,
//     locationServices: true,
//     emergencyAlerts: true
//   });
//   const [formData, setFormData] = useState({
//     fullName: '',
//     email: '',
//     phoneNumber: '',
//     dateOfBirth: '',
//     bloodType: '',
//     allergies: '',
//     medicalConditions: ''
//   });

//   const [emergencyContacts, setEmergencyContacts] = useState([]);

//   // Fetch user profile on mount
//   useEffect(() => {
//     const fetchProfile = async () => {
//       try {
//         setIsLoading(true);
//         const profile = await userApi.getProfile();
//         setFormData({
//           fullName: profile.full_name || '',
//           email: profile.email || '',
//           phoneNumber: profile.phone || '',
//           dateOfBirth: profile.date_of_birth ? profile.date_of_birth.split('T')[0] : '',
//           bloodType: profile.blood_group || '',
//           allergies: profile.allergies || '',
//           medicalConditions: profile.medical_conditions || ''
//         });

//         // Fetch emergency contacts
//         const contacts = await userApi.getEmergencyContacts();
//         setEmergencyContacts(contacts.map(c => ({
//           id: c.id,
//           name: c.name,
//           relationship: c.relation_type || c.relationship,
//           phone: c.phone,
//           isPrimary: c.is_primary
//         })));
//       } catch (err) {
//         setError('Failed to load profile. Please try again.');
//         console.error(err);
//       } finally {
//         setIsLoading(false);
//       }
//     };

//     if (user) {
//       fetchProfile();
//     } else {
//       navigate('/login');
//     }
//   }, [user, navigate]);

//   // Apply theme to document
//   useEffect(() => {
//     document.documentElement.setAttribute('data-theme', theme);
//   }, [theme]);

//   const handleInputChange = (e) => {
//     const { name, value } = e.target;
//     setFormData(prev => ({
//       ...prev,
//       [name]: value
//     }));
//   };

//   const handleSettingChange = (setting) => {
//     setSettings(prev => ({
//       ...prev,
//       [setting]: !prev[setting]
//     }));
//   };

//   const handleThemeChange = (newTheme) => {
//     setTheme(newTheme);
//   };

//   const handleLanguageChange = (e) => {
//     setLanguage(e.target.value);
//   };

//   const handleSaveSettings = () => {
//     setSuccessMessage(`Settings saved!\nTheme: ${theme}\nLanguage: ${language}`);
//     setTimeout(() => setSuccessMessage(null), 3000);
//   };

//   const handleSaveChanges = async () => {
//     setError(null);
//     setSuccessMessage(null);
//     setIsSaving(true);

//     try {
//       const updateData = {
//         full_name: formData.fullName,
//         phone: formData.phoneNumber,
//       };

//       // Only include optional fields if they have values
//       if (formData.dateOfBirth) {
//         updateData.date_of_birth = formData.dateOfBirth;
//       }
//       if (formData.bloodType) {
//         updateData.blood_group = formData.bloodType;
//       }
//       if (formData.allergies) {
//         updateData.allergies = formData.allergies;
//       }
//       if (formData.medicalConditions) {
//         updateData.medical_conditions = formData.medicalConditions;
//       }

//       console.log('Saving profile:', updateData);
//       const result = await userApi.updateProfile(updateData);
//       console.log('Profile saved:', result);

//       setSuccessMessage('✅ Profile updated successfully!');
//       setTimeout(() => setSuccessMessage(null), 4000);
//     } catch (err) {
//       console.error('Profile save error:', err);
//       const errorMsg = err.response?.data?.detail || err.message || 'Failed to save changes';
//       setError(`❌ ${errorMsg}. Please try again.`);
//       setTimeout(() => setError(null), 5000);
//     } finally {
//       setIsSaving(false);
//     }
//   };

//   const handleLogout = async () => {
//     try {
//       await logout();
//       navigate('/login');
//     } catch (err) {
//       console.error('Logout failed:', err);
//     }
//   };

//   const tabs = [
//     { id: 'personal', label: 'Personal Info', icon: (
//       <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
//         <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
//       </svg>
//     )},
//     { id: 'emergency', label: 'Emergency Contacts', icon: (
//       <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
//         <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
//       </svg>
//     )},
//     { id: 'settings', label: 'Settings', icon: (
//       <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
//         <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
//       </svg>
//     )}
//   ];

//   return (
//     <div className="profile-page">
//       {/* Navigation */}
//       <Navbar />

//       {/* Main Content */}
//       <main className="profile-content">
//         <div className="content-container">
//           {/* Header */}
//           <div className="page-header">
//             <h1>Profile & Settings</h1>
//             <p>Manage your personal information and emergency contacts</p>
//           </div>

//           {/* Tab Navigation */}
//           <div className="tab-navigation">
//             {tabs.map(tab => (
//               <button
//                 key={tab.id}
//                 className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
//                 onClick={() => setActiveTab(tab.id)}
//               >
//                 {tab.icon}
//                 {tab.label}
//               </button>
//             ))}
//           </div>

//           {/* Tab Content */}
//           <div className="tab-content">
//             {activeTab === 'personal' && (
//               <div className="personal-info-form">
//                 <h2>Personal Information</h2>

//                 <div className="form-row">
//                   <div className="form-group">
//                     <label>Full Name</label>
//                     <input
//                       type="text"
//                       name="fullName"
//                       value={formData.fullName}
//                       onChange={handleInputChange}
//                       placeholder="Enter your full name"
//                     />
//                   </div>
//                   <div className="form-group">
//                     <label>Email</label>
//                     <input
//                       type="email"
//                       name="email"
//                       value={formData.email}
//                       onChange={handleInputChange}
//                       placeholder="Enter your email"
//                     />
//                   </div>
//                 </div>

//                 <div className="form-row">
//                   <div className="form-group">
//                     <label>Phone Number</label>
//                     <input
//                       type="tel"
//                       name="phoneNumber"
//                       value={formData.phoneNumber}
//                       onChange={handleInputChange}
//                       placeholder="Enter your phone number"
//                     />
//                   </div>
//                   <div className="form-group">
//                     <label>Date of Birth</label>
//                     <input
//                       type="date"
//                       name="dateOfBirth"
//                       value={formData.dateOfBirth}
//                       onChange={handleInputChange}
//                     />
//                   </div>
//                 </div>

//                 <div className="form-row">
//                   <div className="form-group">
//                     <label>Blood Type</label>
//                     <select
//                       name="bloodType"
//                       value={formData.bloodType}
//                       onChange={handleInputChange}
//                     >
//                       <option value="A+">A+</option>
//                       <option value="A-">A-</option>
//                       <option value="B+">B+</option>
//                       <option value="B-">B-</option>
//                       <option value="AB+">AB+</option>
//                       <option value="AB-">AB-</option>
//                       <option value="O+">O+</option>
//                       <option value="O-">O-</option>
//                     </select>
//                   </div>
//                   <div className="form-group">
//                     <label>Allergies</label>
//                     <input
//                       type="text"
//                       name="allergies"
//                       value={formData.allergies}
//                       onChange={handleInputChange}
//                       placeholder="Enter any allergies"
//                     />
//                   </div>
//                 </div>

//                 <div className="form-group full-width">
//                   <label>Medical Conditions</label>
//                   <textarea
//                     name="medicalConditions"
//                     value={formData.medicalConditions}
//                     onChange={handleInputChange}
//                     placeholder="Enter any medical conditions"
//                     rows="4"
//                   ></textarea>
//                 </div>

//                 {/* Success/Error Messages */}
//                 {successMessage && (
//                   <div className="message-box success">
//                     {successMessage}
//                   </div>
//                 )}
//                 {error && (
//                   <div className="message-box error">
//                     {error}
//                   </div>
//                 )}

//                 <button
//                   className="save-btn"
//                   onClick={handleSaveChanges}
//                   disabled={isSaving}
//                 >
//                   {isSaving ? '⏳ Saving...' : '💾 Save Changes'}
//                 </button>
//               </div>
//             )}

//             {activeTab === 'emergency' && (
//               <div className="emergency-contacts-form">
//                 <div className="emergency-header">
//                   <h2>Emergency Contacts</h2>
//                   <button className="add-contact-btn-green">
//                     <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
//                       <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
//                     </svg>
//                     Add Contact
//                   </button>
//                 </div>

//                 {emergencyContacts.map(contact => (
//                   <div key={contact.id} className="contact-card">
//                     <div className="contact-left">
//                       <div className="contact-avatar">
//                         <svg width="24" height="24" viewBox="0 0 24 24" fill="#2563EB">
//                           <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
//                         </svg>
//                       </div>
//                       <div className="contact-info">
//                         <div className="contact-name-row">
//                           <h3>{contact.name}</h3>
//                           {contact.isPrimary && <span className="primary-badge">PRIMARY</span>}
//                         </div>
//                         <p>{contact.relationship}</p>
//                         <span className="contact-phone">{contact.phone}</span>
//                       </div>
//                     </div>
//                     <div className="contact-actions">
//                       <button className="icon-btn edit-icon">
//                         <svg width="18" height="18" viewBox="0 0 24 24" fill="#2563EB">
//                           <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
//                         </svg>
//                       </button>
//                       <button className="icon-btn delete-icon">
//                         <svg width="18" height="18" viewBox="0 0 24 24" fill="#EF4444">
//                           <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
//                         </svg>
//                       </button>
//                     </div>
//                   </div>
//                 ))}

//                 <div className="info-box">
//                   <div className="info-icon">
//                     <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
//                       <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
//                     </svg>
//                   </div>
//                   <div className="info-content">
//                     <h4>Why Emergency Contacts?</h4>
//                     <p>Emergency contacts will be notified automatically in critical situations. Make sure to keep this information up to date.</p>
//                   </div>
//                 </div>
//               </div>
//             )}

//             {activeTab === 'settings' && (
//               <div className="settings-form">
//                 <h2>App Settings</h2>

//                 <div className="setting-item">
//                   <div className="setting-info">
//                     <h3>Push Notifications</h3>
//                     <p>Receive emergency alerts and updates</p>
//                   </div>
//                   <label className="toggle-switch">
//                     <input
//                       type="checkbox"
//                       checked={settings.pushNotifications}
//                       onChange={() => handleSettingChange('pushNotifications')}
//                     />
//                     <span className="slider"></span>
//                   </label>
//                 </div>

//                 <div className="setting-item">
//                   <div className="setting-info">
//                     <h3>Location Services</h3>
//                     <p>Find nearby emergency facilities</p>
//                   </div>
//                   <label className="toggle-switch">
//                     <input
//                       type="checkbox"
//                       checked={settings.locationServices}
//                       onChange={() => handleSettingChange('locationServices')}
//                     />
//                     <span className="slider"></span>
//                   </label>
//                 </div>

//                 <div className="setting-item">
//                   <div className="setting-info">
//                     <h3>Emergency Alerts</h3>
//                     <p>Critical emergency notifications</p>
//                   </div>
//                   <label className="toggle-switch">
//                     <input
//                       type="checkbox"
//                       checked={settings.emergencyAlerts}
//                       onChange={() => handleSettingChange('emergencyAlerts')}
//                     />
//                     <span className="slider"></span>
//                   </label>
//                 </div>

//                 <div className="setting-group">
//                   <label className="setting-label">Language</label>
//                   <select
//                     className="language-select"
//                     value={language}
//                     onChange={handleLanguageChange}
//                   >
//                     <option value="English">English</option>
//                     <option value="Nepali">Nepali</option>
//                     <option value="Hindi">Hindi</option>
//                     <option value="Spanish">Spanish</option>
//                   </select>
//                 </div>

//                 <div className="setting-group">
//                   <label className="setting-label">Theme</label>
//                   <div className="theme-buttons">
//                     <button
//                       className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
//                       onClick={() => handleThemeChange('light')}
//                     >
//                       <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
//                         <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/>
//                       </svg>
//                       Light
//                     </button>
//                     <button
//                       className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
//                       onClick={() => handleThemeChange('dark')}
//                     >
//                       <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
//                         <path d="M9 2c-1.05 0-2.05.16-3 .46 4.06 1.27 7 5.06 7 9.54 0 4.48-2.94 8.27-7 9.54.95.3 1.95.46 3 .46 5.52 0 10-4.48 10-10S14.52 2 9 2z"/>
//                       </svg>
//                       Dark
//                     </button>
//                   </div>
//                 </div>

//                 <button className="save-settings-btn" onClick={handleSaveSettings}>
//                   Save Settings
//                 </button>
//                 <button className="log-out-btn" onClick={handleLogOut}>
//                   Log Out
//                 </button>
//               </div>
//             )}
//           </div>
//         </div>
//       </main>

//       {/* Footer */}
//       <Footer />
//     </div>
//   );
// };

// export default Profile;

// // import React, { useState, useEffect } from "react";
// // import { useNavigate } from "react-router-dom";
// // import Navbar from "../components/Navbar";
// // import Footer from "../components/Footer";
// // import { useAuth } from "../context/AuthContext";
// // import { userApi } from "../api/userApi";
// // import "../styles/Profile.css";
// // import { logoutRequest } from "../api/auth";   // ✅ logout API

// // const Profile = () => {
// //   const [activeTab, setActiveTab] = useState("personal");
// //   const [theme, setTheme] = useState("light");
// //   const [language, setLanguage] = useState("English");
// //   const [isLoading, setIsLoading] = useState(true);
// //   const [isSaving, setIsSaving] = useState(false);
// //   const [error, setError] = useState(null);
// //   const [successMessage, setSuccessMessage] = useState(null);

// //   const { user } = useAuth();
// //   const navigate = useNavigate();

// //   const [settings, setSettings] = useState({
// //     pushNotifications: true,
// //     locationServices: true,
// //     emergencyAlerts: true,
// //   });

// //   const [formData, setFormData] = useState({
// //     fullName: "",
// //     email: "",
// //     phoneNumber: "",
// //     dateOfBirth: "",
// //     bloodType: "",
// //     allergies: "",
// //     medicalConditions: "",
// //   });

// //   const [emergencyContacts, setEmergencyContacts] = useState([]);

// //   // ---------------- FETCH PROFILE ----------------
// //   useEffect(() => {
// //     const fetchProfile = async () => {
// //       try {
// //         setIsLoading(true);
// //         const profile = await userApi.getProfile();

// //         setFormData({
// //           fullName: profile.full_name || "",
// //           email: profile.email || "",
// //           phoneNumber: profile.phone || "",
// //           dateOfBirth: profile.date_of_birth
// //             ? profile.date_of_birth.split("T")[0]
// //             : "",
// //           bloodType: profile.blood_group || "",
// //           allergies: profile.allergies || "",
// //           medicalConditions: profile.medical_conditions || "",
// //         });

// //         const contacts = await userApi.getEmergencyContacts();
// //         setEmergencyContacts(
// //           contacts.map((c) => ({
// //             id: c.id,
// //             name: c.name,
// //             relationship: c.relation_type || c.relationship,
// //             phone: c.phone,
// //             isPrimary: c.is_primary,
// //           }))
// //         );
// //       } catch (err) {
// //         console.error(err);
// //         setError("Failed to load profile. Please try again.");
// //       } finally {
// //         setIsLoading(false);
// //       }
// //     };

// //     if (user) {
// //       fetchProfile();
// //     } else {
// //       navigate("/login");
// //     }
// //   }, [user, navigate]);

// //   // ---------------- THEME ----------------
// //   useEffect(() => {
// //     document.documentElement.setAttribute("data-theme", theme);
// //   }, [theme]);

// //   const handleInputChange = (e) => {
// //     const { name, value } = e.target;
// //     setFormData((prev) => ({ ...prev, [name]: value }));
// //   };

// //   const handleSettingChange = (setting) => {
// //     setSettings((prev) => ({ ...prev, [setting]: !prev[setting] }));
// //   };

// //   const handleThemeChange = (newTheme) => setTheme(newTheme);

// //   const handleLanguageChange = (e) => setLanguage(e.target.value);

// //   const handleSaveSettings = () => {
// //     setSuccessMessage(`Settings saved!`);
// //     setTimeout(() => setSuccessMessage(null), 3000);
// //   };

// //   const handleSaveChanges = async () => {
// //     setError(null);
// //     setSuccessMessage(null);
// //     setIsSaving(true);

// //     try {
// //       const updateData = {
// //         full_name: formData.fullName,
// //         phone: formData.phoneNumber,
// //       };

// //       if (formData.dateOfBirth) updateData.date_of_birth = formData.dateOfBirth;
// //       if (formData.bloodType) updateData.blood_group = formData.bloodType;
// //       if (formData.allergies) updateData.allergies = formData.allergies;
// //       if (formData.medicalConditions)
// //         updateData.medical_conditions = formData.medicalConditions;

// //       await userApi.updateProfile(updateData);

// //       setSuccessMessage("✅ Profile updated successfully!");
// //       setTimeout(() => setSuccessMessage(null), 4000);
// //     } catch (err) {
// //       console.error(err);
// //       const errorMsg =
// //         err.response?.data?.detail || err.message || "Failed to save changes";
// //       setError(`❌ ${errorMsg}`);
// //     } finally {
// //       setIsSaving(false);
// //     }
// //   };

// //   // ---------------- LOGOUT (IMPORTANT PART) ----------------
// //   const handleLogout = async () => {
// //     try {
// //       await logoutRequest();          // calls backend + clears token
// //       navigate("/login");             // redirect to login
// //     } catch (err) {
// //       console.error("Logout failed:", err);
// //       // safety fallback
// //       localStorage.removeItem("access_token");
// //       localStorage.removeItem("user");
// //       navigate("/login");
// //     }
// //   };

// //   // ---------------- UI ----------------
// //   return (
// //     <div className="profile-page">
// //       <Navbar />

// //       <main className="profile-content">
// //         <div className="content-container">
// //           <div className="page-header">
// //             <h1>Profile & Settings</h1>
// //             <p>Manage your personal information and emergency contacts</p>
// //           </div>

// //           {/* Tabs */}
// //           <div className="tab-navigation">
// //             <button onClick={() => setActiveTab("personal")}>Personal</button>
// //             <button onClick={() => setActiveTab("emergency")}>Emergency</button>
// //             <button onClick={() => setActiveTab("settings")}>Settings</button>
// //           </div>

// //           {/* Content */}
// //           <div className="tab-content">
// //             {activeTab === "personal" && (
// //               <div className="personal-info-form">
// //                 <h2>Personal Information</h2>

// //                 <input
// //                   type="text"
// //                   name="fullName"
// //                   placeholder="Full Name"
// //                   value={formData.fullName}
// //                   onChange={handleInputChange}
// //                 />

// //                 <input
// //                   type="email"
// //                   name="email"
// //                   placeholder="Email"
// //                   value={formData.email}
// //                   disabled
// //                 />

// //                 <input
// //                   type="text"
// //                   name="phoneNumber"
// //                   placeholder="Phone"
// //                   value={formData.phoneNumber}
// //                   onChange={handleInputChange}
// //                 />

// //                 {successMessage && (
// //                   <div className="message-box success">{successMessage}</div>
// //                 )}
// //                 {error && <div className="message-box error">{error}</div>}

// //                 <button onClick={handleSaveChanges} disabled={isSaving}>
// //                   {isSaving ? "Saving..." : "Save Changes"}
// //                 </button>
// //               </div>
// //             )}

// //             {activeTab === "settings" && (
// //               <div className="settings-form">
// //                 <h2>App Settings</h2>

// //                 <button onClick={handleSaveSettings}>Save Settings</button>

// //                 {/* ✅ WORKING LOGOUT BUTTON */}
// //                 <button
// //                   className="log-out-btn"
// //                   onClick={handleLogout}
// //                   style={{ marginTop: "20px", background: "red", color: "white" }}
// //                 >
// //                   Log Out
// //                 </button>
// //               </div>
// //             )}
// //           </div>
// //         </div>
// //       </main>

// //       <Footer />
// //     </div>
// //   );
// // };

// // export default Profile;
