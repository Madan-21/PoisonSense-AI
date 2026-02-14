// Protected route component
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const LoadingSpinner = () => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    background: '#f8f9fa'
  }}>
    <div style={{ textAlign: 'center' }}>
      <div style={{
        width: '50px',
        height: '50px',
        border: '4px solid #e0e0e0',
        borderTop: '4px solid #2563eb',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        margin: '0 auto 1rem'
      }}></div>
      <p style={{ color: '#666', fontSize: '1.1rem' }}>Loading...</p>
    </div>
  </div>
);

/**
 * ProtectedRoute - requires authentication.
 * Optionally accepts `allowedRoles` array to restrict by user role.
 * 
 * Usage:
 *   <ProtectedRoute>            → any logged-in user
 *   <ProtectedRoute allowedRoles={['admin']}>  → admin only
 */
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (loading) {
    return <LoadingSpinner />;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role-based access if allowedRoles is specified
  if (allowedRoles && allowedRoles.length > 0) {
    const userRole = user?.role;
    if (!userRole || !allowedRoles.includes(userRole)) {
      // User is logged in but doesn't have the right role — redirect to home
      return <Navigate to="/" replace />;
    }
  }

  // Render the protected component
  return children;
};

export default ProtectedRoute;