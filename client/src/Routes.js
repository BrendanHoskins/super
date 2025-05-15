import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import PrivateRoute from "./routes/PrivateRoute";
import PublicRoute from "./routes/PublicRoute";
import LoginPage from "./components/LoginPage/LoginPage";
import RegistrationPage from "./components/RegistrationPage/RegistrationPage";
import IntegrationsPage from "./components/IntegrationsPage/IntegrationsPage";
import MessagesPage from "./components/MessagesPage/MessagesPage";
import Layout from "./components/common/Layout";

function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path="/" element={<Navigate to="/messages" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegistrationPage />} />
      </Route>

      <Route element={<PrivateRoute />}>
        <Route element={<Layout />}>
          <Route path="/messages" element={<MessagesPage />} />

          <Route path="/integrations" element={<IntegrationsPage />} />

        </Route>
      </Route>
    </Routes>
  );
}

export default AppRoutes;
