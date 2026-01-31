// Axios configuration - API Client Setup
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const { status, data } = error.response;
      
      if (status === 401) {
        // Token expired or invalid - only clear storage, don't auto-redirect
        // Let the auth context handle the redirect
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
      
      // Keep the full error response for better error handling
      return Promise.reject(error);
    } else if (error.request) {
      // Network error
      error.message = 'Network error. Please check your connection.';
      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);

export default api;
