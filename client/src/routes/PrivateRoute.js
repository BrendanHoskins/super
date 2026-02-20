import React, { useState, useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { getAccessToken, initializeAuth } from '../services/AuthService';

const PrivateRoute = () => {
  const [authReady, setAuthReady] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(!!getAccessToken());

  useEffect(() => {
    if (getAccessToken()) {
      setAuthReady(true);
      return;
    }
    // No token in memory/localStorage – try restoring session from refresh cookie (e.g. after closing tab)
    initializeAuth()
      .then((token) => setIsAuthenticated(!!token))
      .finally(() => setAuthReady(true));
  }, []);

  if (!authReady) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        Loading…
      </div>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;