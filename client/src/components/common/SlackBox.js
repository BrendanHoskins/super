import React from "react";
import { Box, Typography, Button } from "@mui/material";
import { styled } from "@mui/system";
import API from "../../api/api";

const SlackIcon = styled("img")({
  width: 40,
  height: 40,
  marginRight: 16,
});

const SlackBox = ({ enabled, onDisconnect, workspaceName }) => {
  const handleConnect = async () => {
    try {
      const response = await API.get("/slack/oauth/install");
      if (response.data && response.data.authUrl) {
        // Redirect the user to Slack's authorization page
        window.location.href = response.data.authUrl;
      } else {
        console.error("Invalid response from server");
      }
    } catch (error) {
      console.error("Error initiating Slack OAuth:", error);
    }
  };

  const handleClick = () => {
    if (enabled) {
      // If already connected, call the disconnect function
      onDisconnect();
    } else {
      // If not connected, initiate the connection process
      handleConnect();
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        padding: 3,
        borderRadius: 2,
        boxShadow: 3,
        bgcolor: enabled ? "success.light" : "background.paper",
        maxWidth: 400,
      }}
    >
      <SlackIcon src="/slack.svg" alt="Slack logo" />
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="h6" component="h2" gutterBottom>
          {enabled ? "Connected to Slack" : "Connect with Slack"}
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          {enabled
            ? `Your workspace is connected to ${workspaceName}.`
            : "Integrate your workspace with Slack to align with stakeholders."}
        </Typography>
        <Button
          variant="contained"
          color={enabled ? "secondary" : "primary"}
          onClick={handleClick}
        >
          {enabled ? "Disconnect" : "Connect"}
        </Button>
      </Box>
    </Box>
  );
};

export default SlackBox;
