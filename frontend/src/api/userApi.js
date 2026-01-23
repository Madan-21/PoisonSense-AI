// User API - Profile and emergency contacts
import api from './axios';

export const userApi = {
  // Get user profile
  getProfile: async () => {
    const response = await api.get('/users/profile');
    return response.data;
  },

  // Update user profile
  updateProfile: async (profileData) => {
    const response = await api.put('/users/profile', profileData);
    return response.data;
  },

  // Change password
  changePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/users/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  },

  // ============ Emergency Contacts ============

  // Get emergency contacts
  getEmergencyContacts: async () => {
    const response = await api.get('/users/emergency-contacts');
    return response.data;
  },

  // Add emergency contact
  addEmergencyContact: async (contactData) => {
    const response = await api.post('/users/emergency-contacts', contactData);
    return response.data;
  },

  // Update emergency contact
  updateEmergencyContact: async (contactId, contactData) => {
    const response = await api.put(`/users/emergency-contacts/${contactId}`, contactData);
    return response.data;
  },

  // Delete emergency contact
  deleteEmergencyContact: async (contactId) => {
    const response = await api.delete(`/users/emergency-contacts/${contactId}`);
    return response.data;
  },
};

export default userApi;
