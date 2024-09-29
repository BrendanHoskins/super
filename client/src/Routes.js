import React from "react";
import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import PrivateRoute from "./routes/PrivateRoute";
import PublicRoute from "./routes/PublicRoute";
import LoginPage from "./components/LoginPage/LoginPage";
import RegistrationPage from "./components/RegistrationPage/RegistrationPage";
import IntegrationsPage from "./components/IntegrationsPage/IntegrationsPage";
import DashboardPage from "./components/DashboardPage/DashboardPage";
import ProductsPage from "./components/ProductsPage/ProductsPage";
import Layout from "./components/common/Layout";
import SlackOauthCallback from "./components/IntegrationsPage/SlackIntegration/SlackOauthCallback";

function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegistrationPage />} />
      </Route>

      <Route element={<PrivateRoute />}>
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />

          <Route path="/integrations" element={<IntegrationsPage />} />
          <Route
            path="/integrations/slack-oauth-callback"
            element={<SlackOauthCallback />}
          />

          <Route path="/products" element={<ProductsPage />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default AppRoutes;
