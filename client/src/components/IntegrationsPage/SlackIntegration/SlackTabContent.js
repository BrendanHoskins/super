import React, { useState, useEffect } from 'react';
import SlackDefaultEmojiPicker from './SlackDefaultEmojiPicker';
import SlackTeam from './SlackTeam';
import API from '../../../api/api';

function SlackTabContent() {
  const [selectedEmojis, setSelectedEmojis] = useState([]);
  const [selectedMembers, setSelectedMembers] = useState([]);
  const [submitStatus, setSubmitStatus] = useState(null);

  const [usersByGroup, setUsersByGroup] = useState({});
  const [slackDefaultEmojis, setSlackDefaultEmojis] = useState(null);
  const [slackCustomEmojis, setSlackCustomEmojis] = useState(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('All');
  const [configExists, setConfigExists] = useState(false);

  useEffect(() => {
    const fetchSlackDataAndConfiguration = async () => {
      try {
        const response = await API.get('/slack/usage/get-slack-data-and-configuration');
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

          // Set selected emojis
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

          // Map configured emojis
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
              return { ...emoji, src };
            } else if (emojiConfig.src) {
              // Use the 'src' data from the configuration
              return {
                id: emojiConfig.id || 'unknown',
                name: emojiConfig.name || 'Unknown Emoji',
                src: emojiConfig.src,
              };
            } else {
              // Placeholder for unknown emojis
              return {
                id: emojiConfig.id || 'unknown',
                name: emojiConfig.name || 'Unknown Emoji',
                src: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAACqG8...',
              };
            }
          });

          setSelectedEmojis(configuredEmojis);
        }
      } catch (error) {
        console.error('Error fetching Slack data and configuration:', error);
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

  const handleSubmit = async () => {
    try {
      await API.post('/slack/usage/submit-slack-configuration', {
        emojis: selectedEmojis,
        members: selectedMembers,
      });
      setSubmitStatus('success');
      setConfigExists(true);
    } catch (error) {
      console.error('Error submitting configuration:', error);
      setSubmitStatus('error');
    }
  };

  // Function to render selected emoji previews
  const renderEmojiPreviews = () => {
    return (
      <div className="selected-emojis">
        <h3>Selected Emojis:</h3>
        {selectedEmojis.length === 0 ? (
          <p>No emojis selected.</p>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            {selectedEmojis.map((emoji, index) => (
              <div key={index} style={{ margin: '5px', textAlign: 'center' }}>
                {emoji.src ? (
                  <img src={emoji.src} alt={emoji.name} style={{ width: '32px', height: '32px' }} />
                ) : (
                  <span style={{ fontSize: '32px' }}>❓</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleTabClick = (tabName) => {
    setActiveTab(tabName);
  };

  // Handle selected members from SlackTeam
  const handleMemberSelect = (selectedUsers) => {
    setSelectedMembers(selectedUsers);
  };

  // Helper function to ensure a value is an array
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

  return (
    <div className="slack-tab-content" style={{ display: 'flex', flexDirection: 'column' }}>
      {configExists ? (
        <div
          style={{
            backgroundColor: '#e6f7ff',
            padding: '10px',
            marginBottom: '20px',
            borderRadius: '5px',
          }}
        >
          <p>Existing configuration loaded. You can modify and resubmit if needed.</p>
        </div>
      ) : (
        <div
          style={{
            backgroundColor: '#ffe6e6',
            padding: '10px',
            marginBottom: '20px',
            borderRadius: '5px',
          }}
        >
          <p>No existing configuration found. Please select emojis and team members to configure.</p>
        </div>
      )}
      {/* Content */}
      <div style={{ display: 'flex' }}>
        {/* Left side: Emoji Picker */}
        <div style={{ width: '50%' }}>
          <h2>Select Emojis</h2>
          <p>Choose emojis to tag messages for syncing with XProd</p>
          <SlackDefaultEmojiPicker
            onEmojiSelect={handleEmojiSelect}
            slackDefaultEmojis={slackDefaultEmojis}
            slackCustomEmojis={slackCustomEmojis}
          />
          {renderEmojiPreviews()}
        </div>
        {/* Right side: Slack Team Members */}
        <div style={{ width: '50%', marginLeft: '20px' }}>
          <h2>Select Team Members</h2>
          <SlackTeam
            usersByGroup={usersByGroup}
            searchTerm={searchTerm}
            activeTab={activeTab}
            onSearch={handleSearch}
            onTabClick={handleTabClick}
            onMemberSelect={handleMemberSelect}
            initialSelectedMembers={selectedMembers}
          />
        </div>
      </div>
      {/* Submit Button */}
      <div style={{ width: '100%', marginTop: '20px' }}>
        <button
          onClick={handleSubmit}
          disabled={selectedEmojis.length === 0 && selectedMembers.length === 0}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
          }}
        >
          {configExists ? 'Update Configuration' : 'Submit Configuration'}
        </button>
        {submitStatus === 'success' && (
          <p style={{ color: 'green' }}>Configuration submitted successfully!</p>
        )}
        {submitStatus === 'error' && (
          <p style={{ color: 'red' }}>Error submitting configuration. Please try again.</p>
        )}
      </div>
    </div>
  );
}

export default SlackTabContent;