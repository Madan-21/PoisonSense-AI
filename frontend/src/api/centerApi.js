// Center API - Hospitals and Poison Centers endpoints
import api from './axios';

export const centerApi = {
  // ============ Hospitals ============
  
  // Find nearby hospitals
  getNearbyHospitals: async (latitude, longitude, options = {}) => {
    const { radiusKm = 50, limit = 10, toxicologyOnly = true } = options;
    
    const response = await api.get('/hospitals/nearby', {
      params: {
        latitude,
        longitude,
        radius_km: radiusKm,
        limit,
        toxicology_only: toxicologyOnly
      }
    });
    return response.data;
  },

  // List all hospitals
  getAllHospitals: async (filters = {}) => {
    const response = await api.get('/hospitals', { params: filters });
    return response.data;
  },

  // Get hospital details
  getHospitalDetails: async (hospitalId) => {
    const response = await api.get(`/hospitals/${hospitalId}`);
    return response.data;
  },

  // Find nearby toxicology labs
  getNearbyLabs: async (latitude, longitude, radiusKm = 50) => {
    const response = await api.get('/labs/nearby', {
      params: { latitude, longitude, radius_km: radiusKm }
    });
    return response.data;
  },
  
  // List all toxicology labs
  getAllLabs: async () => {
    const response = await api.get('/labs/');
    return response.data;
  },

  // ============ Poison Centers ============
  
  // Find nearby poison centers
  getNearbyPoisonCenters: async (latitude, longitude, options = {}) => {
    const { radiusKm = 100, limit = 5 } = options;
    
    const response = await api.get('/poison-centers/nearby', {
      params: {
        latitude,
        longitude,
        radius_km: radiusKm,
        limit
      }
    });
    return response.data;
  },

  // List all poison centers
  getAllPoisonCenters: async (filters = {}) => {
    const response = await api.get('/poison-centers', { params: filters });
    return response.data;
  },

  // Get poison center details
  getPoisonCenterDetails: async (centerId) => {
    const response = await api.get(`/poison-centers/${centerId}`);
    return response.data;
  },

  // ============ Antidotes ============
  
  // Search for antidote availability
  searchAntidote: async (antidoteName, latitude = null, longitude = null) => {
    const params = { antidote_name: antidoteName };
    if (latitude && longitude) {
      params.latitude = latitude;
      params.longitude = longitude;
    }
    
    const response = await api.get('/poison-centers/antidotes/search', { params });
    return response.data;
  },

  // Get all available antidotes
  getAllAntidotes: async () => {
    const response = await api.get('/poison-centers/antidotes/all');
    return response.data;
  },
};

export default centerApi;
