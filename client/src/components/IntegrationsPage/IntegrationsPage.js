import React, { useState, useEffect } from "react";
import { Box, Tab, Tabs, Alert, Snackbar, Typography, Container } from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";
import SlackBox from "../common/SlackBox";
import SlackTabContent from "./SlackIntegration/SlackTabContent";
import API from "../../api/api";

function IntegrationsPage() {
  const [tabValue, setTabValue] = useState(0);
  const [integrations, setIntegrations] = useState({});
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    fetchIntegrations();
    checkForIntegrationStatus();
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

  const checkForIntegrationStatus = () => {
    const params = new URLSearchParams(location.search);
    const success = params.get("success");
    const error = params.get("error");
    const message = params.get("message");

    if (success === "true" || error) {
      const statusKey = `integration_status_${Date.now()}`;
      const statusShown = sessionStorage.getItem(statusKey);

      if (!statusShown) {
        if (success === "true") {
          setSnackbarMessage(message || "Slack integration successful!");
          setSnackbarSeverity("success");
        } else {
          setSnackbarMessage(message || `Error: ${error}`);
          setSnackbarSeverity("error");
        }
        setSnackbarOpen(true);
        sessionStorage.setItem(statusKey, "true");
      }

      // Remove the query parameters from the URL
      navigate(location.pathname, { replace: true });
    }
  };

  const handleSnackbarClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbarOpen(false);
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
    <Container maxWidth="lg" sx={{ pl: 2 }}>
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography 
          variant="h5" 
          component="h1" 
          sx={{ 
            mb: 3, 
            ml: -20,
            fontWeight: 400, 
            color: 'text.secondary',
            textTransform: 'uppercase',
            letterSpacing: '0.1em'
          }}
        >
          Integrations
        </Typography>
        <Snackbar
          open={snackbarOpen}
          autoHideDuration={3500}
          onClose={handleSnackbarClose}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert
            onClose={handleSnackbarClose}
            severity={snackbarSeverity}
            sx={{ width: "100%" }}
          >
            {snackbarMessage}
          </Alert>
        </Snackbar>
        <Box
          sx={{
            borderBottom: 1,
            borderColor: "divider",
            position: "sticky",
            top: 0,
            zIndex: 1,
            backgroundColor: 'white',
            ml: -20, // Align with the header
            pl: 20, // Add padding to compensate for the negative margin
          }}
        >
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange}
            sx={{ ml: -20 }} // Move tabs to the left
          >
            <Tab label="All Integrations" />
            {integrations.slack?.enabled && <Tab label="Slack Settings" />}
          </Tabs>
        </Box>
        <Box sx={{ p: 3, ml: -20 }}>
          {tabValue === 0 && (
            <Box>
              <SlackBox
                enabled={integrations.slack?.enabled || false}
                onDisconnect={handleDisconnectSlack}
                workspaceName={
                  integrations.slack?.installation?.team_name ||
                  integrations.slack?.installation?.enterprise_name
                }
              />
            </Box>
          )}
          {tabValue === 1 && integrations.slack?.enabled && <SlackTabContent />}
        </Box>
      </Box>
    </Container>
  );
}

export default IntegrationsPage;
