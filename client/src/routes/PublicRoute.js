import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { getAccessToken } from '../services/AuthService';

const PublicRoute = () => {
  const isAuthenticated = !!getAccessToken();
  return !isAuthenticated ? <Outlet /> : <Navigate to="/messages" replace />;
};

export default PublicRoute;
