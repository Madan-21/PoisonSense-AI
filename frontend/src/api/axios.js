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

// Retry configuration
const MAX_RETRIES = 2;
const RETRY_DELAY = 1000; // 1 second

// Sleep helper for retry delay
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

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

// Response interceptor - handle errors with retry logic
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    
    // Initialize retry count if not exists
    if (!config.__retryCount) {
      config.__retryCount = 0;
    }
    
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
      // Network error - retry up to MAX_RETRIES times
      if (config.__retryCount < MAX_RETRIES) {
        config.__retryCount += 1;
        console.log(`Retry attempt ${config.__retryCount} of ${MAX_RETRIES} for ${config.url}`);
        
        // Wait before retrying
        await sleep(RETRY_DELAY * config.__retryCount);
        
        // Retry the request
        return api(config);
      }
      
      // Max retries exceeded
      error.message = 'Network error. Please check your connection and try again.';
      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);

export default api;
