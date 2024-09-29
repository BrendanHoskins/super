import React, { useState, useEffect } from "react";
import { Box, Tab, Tabs, Alert, Snackbar } from "@mui/material";
import { useLocation } from "react-router-dom";
import SlackBox from "./SlackIntegration/SlackBox";
import SlackTabContent from "./SlackIntegration/SlackTabContent";
import API from "../../api/api";

function IntegrationsPage() {
  const [tabValue, setTabValue] = useState(0);
  const [integrations, setIntegrations] = useState({});
  const [alertOpen, setAlertOpen] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const [alertSeverity, setAlertSeverity] = useState("success");
  const location = useLocation();

  useEffect(() => {
    fetchIntegrations();
    checkForMessages();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchIntegrations = async () => {
    try {
      const response = await API.get("/integrations/connected-integrations");
      setIntegrations(response.data);
    } catch (error) {
      console.error("Error fetching integrations:", error);
    }
  };

  const checkForMessages = () => {
    if (location.state) {
      const { success, error, message } = location.state;
      if (success) {
        setAlertMessage(message || "Operation successful!");
        setAlertSeverity("success");
        setAlertOpen(true);
      } else if (error) {
        setAlertMessage(message || "An error occurred.");
        setAlertSeverity("error");
        setAlertOpen(true);
      }
      // Clear the location state
      window.history.replaceState({}, document.title);
    }
  };

  const handleAlertClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setAlertOpen(false);
  };

  const handleDisconnectSlack = async () => {
    try {
      await API.post("/slack/oauth/uninstall");
      fetchIntegrations();
    } catch (error) {
      console.error("Error disconnecting Slack:", error);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Box sx={{ width: "100%", typography: "body1" }}>
      <Snackbar
        open={alertOpen}
        autoHideDuration={6000}
        onClose={handleAlertClose}
      >
        <Alert
          onClose={handleAlertClose}
          severity={alertSeverity}
          sx={{ width: "100%" }}
        >
          {alertMessage}
        </Alert>
      </Snackbar>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="All Integrations" />
          {integrations.slack?.enabled && <Tab label="Slack Settings" />}
        </Tabs>
      </Box>
      <Box sx={{ p: 3 }}>
        {tabValue === 0 && (
          <Box>
            <SlackBox
              enabled={integrations.slack?.enabled || false}
              onDisconnect={handleDisconnectSlack}
              workspaceName={integrations.slack?.installation?.team_name || integrations.slack?.installation?.enterprise_name}
            />
          </Box>
        )}
        {tabValue === 1 && integrations.slack?.enabled && (
          <SlackTabContent />
        )}
      </Box>
    </Box>
  );
}

export default IntegrationsPage;
