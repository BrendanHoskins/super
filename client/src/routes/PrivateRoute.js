import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { getAccessToken } from '../services/AuthService';

const PrivateRoute = () => {
  const isAuthenticated = !!getAccessToken();

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;