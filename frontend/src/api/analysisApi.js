// Analysis API - AI Poison Analysis endpoints (Agentic AI)
import api from './axios';

export const analysisApi = {
  // ==========================================
  // AGENTIC AI CHAT INTERFACE
  // ==========================================
  
  // Main chat endpoint for agentic AI
  chatWithAgent: async (message, options = {}) => {
    const { latitude, longitude, sessionId } = options;
    
    const requestData = {
      message: message,
    };
    
    if (latitude && longitude) {
      requestData.latitude = latitude;
      requestData.longitude = longitude;
    }
    
    if (sessionId) {
      requestData.session_id = sessionId;
    }
    
    const response = await api.post('/agent/chat', requestData);
    return response.data;
  },

  // Legacy analyze symptoms endpoint (still works)
  analyzeSymptoms: async (symptoms, options = {}) => {
    const { latitude, longitude, age, weightKg, timeSinceExposure, suspectedSubstance, exposureRoute, sessionId } = options;
    
    // Use new agentic chat endpoint
    const requestData = {
      message: symptoms,
    };
    
    if (latitude && longitude) {
      requestData.latitude = latitude;
      requestData.longitude = longitude;
    }
    
    if (sessionId) {
      requestData.session_id = sessionId;
    }
    
    const response = await api.post('/agent/chat', requestData);
    return response.data;
  },

  // ==========================================
  // AGENTIC AI TOOL ENDPOINTS
  // ==========================================
  
  // Analyze symptoms specifically
  analyzeSymptomsTool: async (symptoms) => {
    const response = await api.post('/agent/analyze-symptoms', { symptoms });
    return response.data;
  },

  // Assess severity
  assessSeverity: async (symptoms, poisonName = null) => {
    const requestData = { symptoms };
    if (poisonName) requestData.poison_name = poisonName;
    
    const response = await api.post('/agent/assess-severity', requestData);
    return response.data;
  },

  // Search poison database
  searchPoisons: async (query) => {
    const response = await api.post('/agent/search-poisons', { query });
    return response.data;
  },

  // Get poison information
  getPoisonInfo: async (poisonName) => {
    const response = await api.get(`/agent/poison/${encodeURIComponent(poisonName)}`);
    return response.data;
  },

  // Get first aid instructions
  getFirstAid: async (poisonName) => {
    const response = await api.get(`/agent/poison/${encodeURIComponent(poisonName)}/first-aid`);
    return response.data;
  },

  // Get antidote information
  getAntidote: async (poisonName) => {
    const response = await api.get(`/agent/poison/${encodeURIComponent(poisonName)}/antidote`);
    return response.data;
  },

  // Get management protocol
  getManagementProtocol: async (poisonName) => {
    const response = await api.get(`/agent/poison/${encodeURIComponent(poisonName)}/protocol`);
    return response.data;
  },

  // Find nearby hospitals
  findNearbyHospitals: async (latitude = null, longitude = null, antidote = null) => {
    const params = {};
    if (latitude) params.latitude = latitude;
    if (longitude) params.longitude = longitude;
    if (antidote) params.antidote = antidote;
    
    const response = await api.get('/agent/hospitals/nearby', { params });
    return response.data;
  },

  // Find nearby poison centers
  findNearbyPoisonCenters: async (latitude = null, longitude = null) => {
    const params = {};
    if (latitude) params.latitude = latitude;
    if (longitude) params.longitude = longitude;
    
    const response = await api.get('/agent/poison-centers/nearby', { params });
    return response.data;
  },

  // Get emergency numbers
  getEmergencyNumbers: async (country = 'nepal') => {
    const response = await api.get('/agent/emergency-numbers', { params: { country } });
    return response.data;
  },

  // List all poisons
  listAllPoisons: async () => {
    const response = await api.get('/agent/poisons/list');
    return response.data;
  },

  // Get poison categories
  getPoisonCategories: async () => {
    const response = await api.get('/agent/categories');
    return response.data;
  },

  // ==========================================
  // SESSION MANAGEMENT
  // ==========================================
  
  // End chat session
  endSession: async (sessionId) => {
    const response = await api.delete(`/agent/session/${sessionId}`);
    return response.data;
  },

  // Get session summary
  getSessionSummary: async (sessionId) => {
    const response = await api.get(`/agent/session/${sessionId}/summary`);
    return response.data;
  },

  // ==========================================
  // LEGACY ENDPOINTS (for backward compatibility)
  // ==========================================

  // Get user's analysis history
  getHistory: async (limit = 20) => {
    const response = await api.get('/analysis/history', {
      params: { limit }
    });
    return response.data;
  },

  // Get AI model information
  getModelInfo: async () => {
    const response = await api.get('/analysis/model-info');
    return response.data;
  },

  // Get list of all known poisons (legacy)
  getAllPoisons: async (category = null) => {
    const params = category ? { category } : {};
    const response = await api.get('/analysis/poisons', { params });
    return response.data;
  },

  // Get detailed poison information (legacy)
  getPoisonDetails: async (poisonId) => {
    const response = await api.get(`/analysis/poisons/${poisonId}`);
    return response.data;
  },
};

export default analysisApi;
