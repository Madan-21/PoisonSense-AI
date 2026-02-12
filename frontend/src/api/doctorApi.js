// Doctor API - Doctor registration and verification endpoints
import api from './axios';

export const doctorApi = {
  // Register as a doctor
  registerDoctor: async (doctorData) => {
    const response = await api.post('/doctors/register', doctorData);
    return response.data;
  },

  // List verified doctors
  getVerifiedDoctors: async (filters = {}) => {
    const response = await api.get('/doctors', { params: filters });
    return response.data;
  },

  // Get doctor details
  getDoctorDetails: async (doctorId) => {
    const response = await api.get(`/doctors/${doctorId}`);
    return response.data;
  },

  // Get my doctor profile (for doctors only)
  getMyProfile: async () => {
    const response = await api.get('/doctors/me/profile');
    return response.data;
  },

  // Update my doctor profile
  updateMyProfile: async (profileData) => {
    const response = await api.put('/doctors/me/profile', profileData);
    return response.data;
  },

  // ============ Admin Only ============
  
  // Get pending verifications (admin)
  getPendingVerifications: async () => {
    const response = await api.get('/doctors/pending-verification');
    return response.data;
  },

  // Verify/reject doctor (admin)
  verifyDoctor: async (doctorId, status, notes = null) => {
    const response = await api.put(`/doctors/${doctorId}/verify`, {
      status,
      verification_notes: notes
    });
    return response.data;
  },
};

export default doctorApi;
