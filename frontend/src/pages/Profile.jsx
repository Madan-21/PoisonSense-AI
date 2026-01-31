import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';
import { userApi } from '../api/userApi';
import { getErrorMessage } from '../utils/errorHandler';
import '../styles/Profile.css';

const Profile = () => {
  const [activeTab, setActiveTab] = useState('personal');
  const [theme, setTheme] = useState('light');
  const [language, setLanguage] = useState('English');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  
  const { user, logout, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [settings, setSettings] = useState({
    pushNotifications: true,
    locationServices: true,
    emergencyAlerts: true
  });
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phoneNumber: '',
    dateOfBirth: '',
    bloodType: '',
    allergies: '',
    medicalConditions: ''
  });

  const [emergencyContacts, setEmergencyContacts] = useState([]);
  const [showAddContactModal, setShowAddContactModal] = useState(false);
  const [newContact, setNewContact] = useState({
    name: '',
    relationship: '',
    phone: '',
    isPrimary: false
  });

  // Fetch user profile on mount
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setIsLoading(true);
        const profile = await userApi.getProfile();
        
        console.log('Profile loaded from API:', {
          dateOfBirth: profile.date_of_birth,
          formatted: profile.date_of_birth ? profile.date_of_birth.split('T')[0] : ''
        });
        
        setFormData({
          fullName: profile.full_name || '',
          email: profile.email || '',
          phoneNumber: profile.phone || '',
          dateOfBirth: profile.date_of_birth ? profile.date_of_birth.split('T')[0] : '',
          bloodType: profile.blood_group || '',
          allergies: profile.allergies || '',
          medicalConditions: profile.medical_conditions || ''
        });
        
        // Fetch emergency contacts
        const contacts = await userApi.getEmergencyContacts();
        setEmergencyContacts(contacts.map(c => ({
          id: c.id,
          name: c.name,
          relationship: c.relation_type || c.relationship,
          phone: c.phone,
          isPrimary: c.is_primary
        })));
      } catch (err) {
        setError('Failed to load profile. Please try again.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    
    // Only redirect if auth is not loading and there's no user
    if (!authLoading && !user) {
      navigate('/login');
      return;
    }
    
    if (user) {
      fetchProfile();
    }
  }, [user, navigate, authLoading]);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
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
  };

  const handleSettingChange = (setting) => {
    setSettings(prev => ({
      ...prev,
      [setting]: !prev[setting]
    }));
  };

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleSaveSettings = () => {
    setSuccessMessage(`Settings saved!\nTheme: ${theme}\nLanguage: ${language}`);
    setTimeout(() => setSuccessMessage(null), 3000);
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
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Logout failed:', err);
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
    { id: 'personal', label: 'Personal Info', icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
      </svg>
    )},
    { id: 'emergency', label: 'Emergency Contacts', icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
      </svg>
    )},
    { id: 'settings', label: 'Settings', icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
      </svg>
    )}
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
      {/* Navigation */}
      <Navbar />

      {/* Main Content */}
      <main className="profile-content">
        <div className="content-container">
          {/* Header */}
          <div className="page-header">
            <h1>Profile & Settings</h1>
            <p>Manage your personal information and emergency contacts</p>
          </div>

          {/* Tab Navigation */}
          <div className="tab-navigation">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'personal' && (
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
                      placeholder="Enter your full name"
                    />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="Enter your email"
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
                  </button>
                </div>
                
                {emergencyContacts.map(contact => (
                  <div key={contact.id} className="contact-card">
                    <div className="contact-left">
                      <div className="contact-avatar">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#2563EB">
                          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                        </svg>
                      </div>
                      <div className="contact-info">
                        <div className="contact-name-row">
                          <h3>{contact.name}</h3>
                          {contact.isPrimary && <span className="primary-badge">PRIMARY</span>}
                        </div>
                        <p>{contact.relationship}</p>
                        <span className="contact-phone">{contact.phone}</span>
                      </div>
                    </div>
                    <div className="contact-actions">
                      <button 
                        className="icon-btn delete-icon"
                        onClick={() => handleDeleteContact(contact.id)}
                        title="Delete contact"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="#EF4444">
                          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
                
                <div className="info-box">
                  <div className="info-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
                    </svg>
                  </div>
                  <div className="info-content">
                    <h4>Why Emergency Contacts?</h4>
                    <p>Emergency contacts will be notified automatically in critical situations. Make sure to keep this information up to date.</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
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
                      onChange={() => handleSettingChange('pushNotifications')}
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
                      onChange={() => handleSettingChange('locationServices')}
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
                      onChange={() => handleSettingChange('emergencyAlerts')}
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
                      className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
                      onClick={() => handleThemeChange('light')}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/>
                      </svg>
                      Light
                    </button>
                    <button 
                      className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
                      onClick={() => handleThemeChange('dark')}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M9 2c-1.05 0-2.05.16-3 .46 4.06 1.27 7 5.06 7 9.54 0 4.48-2.94 8.27-7 9.54.95.3 1.95.46 3 .46 5.52 0 10-4.48 10-10S14.52 2 9 2z"/>
                      </svg>
                      Dark
                    </button>
                  </div>
                </div>

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
      <Footer />
    </div>
  );
};

export default Profile;
