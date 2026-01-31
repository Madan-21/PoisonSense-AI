// Auth context - Authentication state management with Email Verification
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/authApi';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pendingVerification, setPendingVerification] = useState(null); // { email, message }

  // Check for existing session on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedUser = authApi.getStoredUser();
        const token = localStorage.getItem('access_token');
        
        if (storedUser && token) {
          // Try to validate token by fetching current user
          try {
            const currentUser = await authApi.getCurrentUser();
            setUser(currentUser);
            // Update stored user in case data changed
            localStorage.setItem('user', JSON.stringify(currentUser));
          } catch (err) {
            // Token is invalid or expired
            console.log('Token validation failed:', err.message);
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            setUser(null);
          }
        }
      } catch (err) {
        console.error('Auth initialization error:', err);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // Login function
  const login = async (email, password) => {
    setError(null);
    try {
      const response = await authApi.login(email, password);
      setUser(response.user);
      setPendingVerification(null);
      return response;
    } catch (err) {
      // Check if email verification is required
      if (err.response?.status === 403 && err.response?.data?.detail?.includes('not verified')) {
        setPendingVerification({ email, message: err.response.data.detail });
        throw new Error('Email verification required');
      }
      setError(err.message);
      throw err;
    }
  };

  // Signup function - now returns pending verification
  const signup = async (userData) => {
    setError(null);
    try {
      const response = await authApi.signup(userData);
      // Set pending verification state
      setPendingVerification({ 
        email: response.email, 
        message: response.message 
      });
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  // Verify OTP function
  const verifyOTP = async (email, otp) => {
    setError(null);
    try {
      const response = await authApi.verifyOTP(email, otp);
      if (response.verified && response.user) {
        setUser(response.user);
        setPendingVerification(null);
      }
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  // Resend OTP function
  const resendOTP = async (email) => {
    setError(null);
    try {
      const response = await authApi.resendOTP(email);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  // Clear pending verification
  const clearPendingVerification = () => {
    setPendingVerification(null);
  };

  // Logout function
  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      setUser(null);
      setPendingVerification(null);
    }
  };

  // Refresh user data
  const refreshUser = async () => {
    try {
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
      localStorage.setItem('user', JSON.stringify(currentUser));
    } catch (err) {
      console.error('Failed to refresh user:', err);
    }
  };

  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    pendingVerification,
    login,
    signup,
    verifyOTP,
    resendOTP,
    clearPendingVerification,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
