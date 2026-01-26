// Antidotes and Poison Management API
import api from './axios';

export const antidoteApi = {
  // Get poison-antidote mapping
  getPoisonAntidoteMap: async (category = null) => {
    const params = category ? { category } : {};
    const response = await api.get('/antidotes/poison-antidote-map', { params });
    return response.data;
  },

  // Find antidote locations
  findAntidoteLocations: async (antidoteName, latitude, longitude, radiusKm = 100) => {
    const response = await api.get(`/antidotes/find-antidote/${encodeURIComponent(antidoteName)}`, {
      params: { latitude, longitude, radius_km: radiusKm }
    });
    return response.data;
  },

  // Get management protocol for a specific poison
  getManagementProtocol: async (poisonName, severity = null) => {
    const params = severity ? { severity } : {};
    const response = await api.get(`/antidotes/management-protocol/${encodeURIComponent(poisonName)}`, { params });
    return response.data;
  }
};

export const labApi = {
  // List all toxicology labs
  getAllLabs: async (city = null, testType = null, is24Hours = null) => {
    const params = {};
    if (city) params.city = city;
    if (testType) params.test_type = testType;
    if (is24Hours !== null) params.is_24_hours = is24Hours;
    
    const response = await api.get('/labs/', { params });
    return response.data;
  },

  // Find nearby labs
  findNearbyLabs: async (latitude, longitude, radiusKm = 50, testType = null) => {
    const params = { latitude, longitude, radius_km: radiusKm };
    if (testType) params.test_type = testType;
    
    const response = await api.get('/labs/nearby', { params });
    return response.data;
  },

  // Get test catalog
  getTestsCatalog: async () => {
    const response = await api.get('/labs/tests-catalog');
    return response.data;
  }
};

export default { antidoteApi, labApi };
