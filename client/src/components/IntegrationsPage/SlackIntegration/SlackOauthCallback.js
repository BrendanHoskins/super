import React, { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";

function SlackOauthCallback() {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Parse query parameters
    const params = new URLSearchParams(location.search);
    const success = params.get('success');
    const error = params.get('error');

    // Redirect to IntegrationsPage with state
    navigate('/integrations', { 
      state: { 
        success: success === 'true', 
        error: error, 
        message: success === 'true' ? 'Slack integration successful!' : error 
      },
      replace: true
    });
  }, [location, navigate]);

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <CircularProgress />
    </Box>
  );
}

export default SlackOauthCallback;