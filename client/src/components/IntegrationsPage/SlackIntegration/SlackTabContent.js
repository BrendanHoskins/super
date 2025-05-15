import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Snackbar, Alert, Paper, CircularProgress } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import SlackDefaultEmojiPicker from './SlackTabContentEmojiPicker';
import SlackTeam from './SlackTabContentTeamMemberSelection';
import SlackConfiguration from './SlackTabContentSelectedConfiguration';
import API from '../../../api/api';

function SlackTabContent() {
  const [selectedEmojis, setSelectedEmojis] = useState([]);
  const [selectedMembers, setSelectedMembers] = useState([]);

  const [usersByGroup, setUsersByGroup] = useState({});
  const [slackDefaultEmojis, setSlackDefaultEmojis] = useState(null);
  const [slackCustomEmojis, setSlackCustomEmojis] = useState(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('All');
  const [configExists, setConfigExists] = useState(false);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success',
  });
  const [initialConfig, setInitialConfig] = useState({ emojis: [], members: [] });

  useEffect(() => {
    const fetchSlackDataAndConfiguration = async () => {
      setLoading(true);
      try {
        const response = await API.get('slack/usage/get-slack-data-and-configuration');
        const data = response.data;

        // Set users data
        setUsersByGroup(data.slack_users);

        // Set emojis data
        setSlackDefaultEmojis(data.slack_emojis.slack_default_emojis);
        setSlackCustomEmojis(data.slack_emojis.slack_custom_emojis);

        // Handle existing configuration
        const config = data.slack_configuration;
        if (
          config &&
          (config.slack_emoji_configuration.length > 0 ||
            config.slack_team_configuration.length > 0)
        ) {
          setConfigExists(true);

          // Map user IDs to user objects for quick lookup
          const allUsers = Object.values(data.slack_users).flat();
          const userDict = {};
          allUsers.forEach((user) => {
            userDict[user.id] = user;
          });

          const configuredMembers = config.slack_team_configuration
            .map((member) => userDict[member.id])
            .filter((user) => user !== undefined);
          setSelectedMembers(configuredMembers);

          // Build emoji dictionary for easy lookup
          const emojiDict = {};

          // Combine default emojis into emojiDict
          if (data.slack_emojis.slack_default_emojis) {
            Object.entries(data.slack_emojis.slack_default_emojis.emojis).forEach(
              ([key, value]) => {
                const shortcodesArray = ensureArray(value.shortcodes);

                const emojiData = {
                  id: key,
                  ...value,
                  shortcodes: shortcodesArray,
                };

                // Add multiple keys for better matching
                const keys = [key, value.unified, value.name, ...shortcodesArray].filter(Boolean);

                keys.forEach((k) => {
                  emojiDict[k] = emojiData;
                });
              }
            );
          }

          // Combine custom emojis into emojiDict
          if (data.slack_emojis.slack_custom_emojis) {
            data.slack_emojis.slack_custom_emojis.forEach((category) => {
              category.emojis.forEach((emoji) => {
                const shortcodesArray = ensureArray(emoji.shortcodes);

                const emojiData = {
                  ...emoji,
                  shortcodes: shortcodesArray,
                };

                // Add multiple keys for better matching
                const keys = [emoji.id, emoji.name, ...shortcodesArray].filter(Boolean);

                keys.forEach((k) => {
                  emojiDict[k] = emojiData;
                });
              });
            });
          }

          // Map configured emojis and ensure 'shortcodes' are properly set
          const configuredEmojis = config.slack_emoji_configuration.map((emojiConfig) => {
            // Ensure 'shortcodes' is an array
            const shortcodesArray = ensureArray(emojiConfig.shortcodes);

            // Attempt to match emoji using multiple identifiers
            const emojiIdCandidates = [
              emojiConfig.id,
              emojiConfig.unified,
              emojiConfig.name,
              ...shortcodesArray,
            ].filter(Boolean);

            let emoji = null;

            for (let id of emojiIdCandidates) {
              if (emojiDict[id]) {
                emoji = emojiDict[id];
                break;
              }
            }

            if (emoji) {
              // Ensure 'src' is set, prioritize emojiConfig.src
              const src = emojiConfig.src || emoji.src || emoji.imageUrl;

              // Combine shortcodes from emoji and emojiConfig
              const emojiShortcodes = ensureArray(emoji.shortcodes);
              const emojiConfigShortcodes = shortcodesArray;
              const combinedShortcodes = [...new Set([...emojiShortcodes, ...emojiConfigShortcodes])];

              // Return processed emoji
              return { ...emoji, src, shortcodes: combinedShortcodes };
            } else if (emojiConfig.src) {
              // Use the 'src' data from the configuration
              return {
                id: emojiConfig.id || 'unknown',
                name: emojiConfig.name || 'Unknown Emoji',
                src: emojiConfig.src,
                shortcodes: shortcodesArray,
              };
            } else {
              // Placeholder for unknown emojis
              return {
                id: emojiConfig.id || 'unknown',
                name: emojiConfig.name || 'Unknown Emoji',
                src: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAACqG8...',
                shortcodes: shortcodesArray,
              };
            }
          });

          // Ensure all configured emojis have 'shortcodes' properly set
          const processedConfiguredEmojis = configuredEmojis.map((emoji) => ({
            ...emoji,
            shortcodes: ensureArray(emoji.shortcodes),
          }));

          setSelectedEmojis(processedConfiguredEmojis);

          // Store the initial configuration
          setInitialConfig({
            emojis: processedConfiguredEmojis,
            members: configuredMembers,
          });
        }
      } catch (error) {
        console.error('Error fetching Slack data and configuration:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSlackDataAndConfiguration();
  }, []);

  const handleEmojiSelect = (emoji) => {
    let processedEmoji = { ...emoji };

    // Ensure that 'shortcodes' is an array
    processedEmoji.shortcodes = ensureArray(processedEmoji.shortcodes);

    if (!processedEmoji.src && processedEmoji.native) {
      const canvas = document.createElement('canvas');
      canvas.width = 72; // Slightly larger canvas
      canvas.height = 72;
      const ctx = canvas.getContext('2d');
      ctx.font = '64px serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(processedEmoji.native, canvas.width / 2, canvas.height / 2 + 2); // Slight offset
      const dataURL = canvas.toDataURL('image/png');
      processedEmoji.src = dataURL;
    }

    // Avoid duplicate selection
    setSelectedEmojis((prevEmojis) => {
      const isAlreadySelected = prevEmojis.find((e) => e.id === processedEmoji.id);
      if (!isAlreadySelected) {
        return [...prevEmojis, processedEmoji];
      }
      return prevEmojis;
    });
  };

  // Function to remove an emoji from selectedEmojis
  const handleEmojiRemove = (emojiId) => {
    setSelectedEmojis((prevEmojis) =>
      prevEmojis.filter((emoji) => emoji.id !== emojiId)
    );
  };

  // Function to remove a member from selectedMembers
  const handleMemberRemove = (memberId) => {
    setSelectedMembers((prevMembers) =>
      prevMembers.filter((member) => member.id !== memberId)
    );
  };

  const handleSubmit = async () => {
    try {
      // Ensure all emojis have 'shortcodes' properly set before submitting
      const processedEmojis = selectedEmojis.map((emoji) => ({
        ...emoji,
        shortcodes: ensureArray(emoji.shortcodes),
      }));

      await API.post('slack/usage/submit-slack-configuration', {
        emojis: processedEmojis,
        members: selectedMembers,
      });
      setConfigExists(true);
      setSnackbar({
        open: true,
        message: 'Configuration submitted successfully!',
        severity: 'success',
      });

      // Update the initialConfig state with the new configuration
      setInitialConfig({
        emojis: processedEmojis,
        members: selectedMembers,
      });
    } catch (error) {
      console.error('Error submitting configuration:', error);
      setSnackbar({
        open: true,
        message: 'Error submitting configuration. Please try again.',
        severity: 'error',
      });
    }
  };

  const handleSnackbarClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbar({ ...snackbar, open: false });
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleTabClick = (tabName) => {
    setActiveTab(tabName);
  };

  const handleMemberSelect = (selectedUsers) => {
    setSelectedMembers(selectedUsers);
  };

  const ensureArray = (value) => {
    if (Array.isArray(value)) {
      return value;
    } else if (typeof value === 'string') {
      return value.split(/[:,\s]+/).map((s) => s.trim()).filter(Boolean);
    } else if (value == null) {
      return [];
    } else {
      return [value];
    }
  };

  // Function to check if the current configuration is different from the initial one
  const isConfigChanged = () => {
    if (selectedEmojis.length !== initialConfig.emojis.length || 
        selectedMembers.length !== initialConfig.members.length) {
      return true;
    }

    const emojiIdsMatch = selectedEmojis.every(emoji => 
      initialConfig.emojis.some(initialEmoji => initialEmoji.id === emoji.id)
    );
    const memberIdsMatch = selectedMembers.every(member => 
      initialConfig.members.some(initialMember => initialMember.id === member.id)
    );

    return !emojiIdsMatch || !memberIdsMatch;
  };

  const isUpdateDisabled = () => {
    return (
      selectedEmojis.length === 0 ||
      selectedMembers.length === 0 ||
      (configExists && !isConfigChanged())
    );
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        sx={{
          height: '550px', // Adjust this value to match the approximate height of your tab content
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box display="flex" flexDirection="column" sx={{ height: '100%' }}>
      <Paper elevation={2} sx={{ mb: 3, p: 2, backgroundColor: 'white' }}>
        <Box display="flex" alignItems="center">
          <InfoIcon color="primary" sx={{ mr: 2 }} />
          <Typography variant="body1">
            Super will pull a Slack message when a selected user tags a message with a selected emoji. (Note: only applies to channels and conversations you are a part of)
          </Typography>
        </Box>
      </Paper>

      {/* Content */}
      <Box display="flex" flex="1" sx={{ height: '100%' }}>
        {/* Left side: Emoji Picker */}
        <Box flex="1" display="flex" flexDirection="column" mr={2}>
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <SlackDefaultEmojiPicker
              onEmojiSelect={handleEmojiSelect}
              slackDefaultEmojis={slackDefaultEmojis}
              slackCustomEmojis={slackCustomEmojis}
            />
          </Box>
        </Box>
        {/* Right side: Slack Team Members */}
        <Box flex="1" display="flex" flexDirection="column" ml={2}>
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <SlackTeam
              usersByGroup={usersByGroup}
              searchTerm={searchTerm}
              activeTab={activeTab}
              onSearch={handleSearch}
              onTabClick={handleTabClick}
              onMemberSelect={handleMemberSelect}
              initialSelectedMembers={selectedMembers}
            />
          </Box>
        </Box>
      </Box>
      {/* Configuration */}
      <Box mt={2}>
        <SlackConfiguration
          selectedEmojis={selectedEmojis}
          selectedMembers={selectedMembers}
          handleEmojiRemove={handleEmojiRemove}
          handleMemberRemove={handleMemberRemove} // Pass the new function
        />
      </Box>
      {/* Submit Button */}
      <Box mt={2} display="flex" justifyContent="center">
        <Button
          variant="contained"
          color="primary"
          onClick={handleSubmit}
          disabled={isUpdateDisabled()}
        >
          {configExists ? 'Update Configuration' : 'Submit Configuration'}
        </Button>
      </Box>

      {/* Snackbar for success/error messages */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default SlackTabContent;