// src/api/axios.js
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// ✅ Request interceptor - add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // ✅ custom flag default false
    // (so we can skip special handling in some calls like logout)
    if (config.skipAuthRedirect === undefined) {
      config.skipAuthRedirect = false;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ✅ Response interceptor - keep REAL axios error
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status } = error.response;

      // ✅ Auto clear token on 401 (but don’t force redirect)
      if (status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");

        // ✅ If you want redirect ONLY when NOT logout:
        // (logout request may return 401 if token already expired)
        const skip = error.config?.skipAuthRedirect;
        if (!skip) {
          // Send user to HOME (not login)
          window.location.href = "/";
        }
      }
    }

    // ✅ IMPORTANT: don't wrap into new Error()
    return Promise.reject(error);
  }
);

export default api;
