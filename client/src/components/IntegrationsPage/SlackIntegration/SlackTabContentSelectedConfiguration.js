import React from 'react';
import {
  Box,
  Typography,
  Avatar,
  IconButton,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

function SlackConfiguration({
  selectedEmojis,
  selectedMembers,
  handleEmojiRemove,
  handleMemberRemove,
}) {
  // Function to render emojis
  const renderEmojis = () => {
    if (selectedEmojis.length === 0) {
      return null;
    }

    return (
      <Box display="flex" flexWrap="wrap">
        {selectedEmojis.map((emoji, index) => (
          <Box key={index} position="relative" m={0.5}>
            {emoji.src ? (
              <Avatar
                src={emoji.src}
                alt={emoji.name}
                sx={{ width: 32, height: 32 }}
              />
            ) : (
              <Avatar sx={{ width: 32, height: 32 }}>
                {emoji.native ? emoji.native : '?'}
              </Avatar>
            )}
            <IconButton
              size="small"
              sx={{
                position: 'absolute',
                top: -8,
                right: -8,
                backgroundColor: 'white',
                color: 'grey.700',
                border: '1px solid',
                borderColor: 'grey.400',
              }}
              onClick={() => handleEmojiRemove(emoji.id)}
            >
              <CloseIcon sx={{ fontSize: 12 }} />
            </IconButton>
          </Box>
        ))}
      </Box>
    );
  };

  // Updated function to render team members with emojis
  const renderTeamMembersWithEmojis = () => {
    if (selectedMembers.length === 0) {
      return null;
    }

    return (
      <Box display="flex" flexWrap="wrap">
        {selectedMembers.map((member) => (
          <Box
            key={member.id}
            display="flex"
            alignItems="center"
            m={1}
            p={1}
            border="1px solid"
            borderColor="grey.300"
            borderRadius={2}
          >
            <IconButton
              size="small"
              onClick={() => handleMemberRemove(member.id)}
              sx={{ mr: 1 }}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
            <Avatar
              src={member.profile.image_32 || member.profile.image_72}
              sx={{ width: 32, height: 32, mr: 1 }}
            />
            <Typography variant="body2">
              {member.profile.real_name || member.name}
            </Typography>
            {selectedEmojis.length > 0 && (
              <Box display="flex" ml={1}>
                {selectedEmojis.map((emoji, index) => (
                  <Box key={index} mr={0.5} position="relative">
                    {emoji.src ? (
                      <Avatar
                        src={emoji.src}
                        alt={emoji.name}
                        sx={{ width: 20, height: 20 }}
                      />
                    ) : (
                      <Avatar
                        sx={{ width: 20, height: 20, fontSize: '0.75rem' }}
                      >
                        {emoji.native ? emoji.native : '?'}
                      </Avatar>
                    )}
                    <IconButton
                      size="small"
                      sx={{
                        position: 'absolute',
                        top: -8,
                        right: -8,
                        backgroundColor: 'white',
                        color: 'grey.700',
                        border: '1px solid',
                        borderColor: 'grey.400',
                        padding: '2px',
                      }}
                      onClick={() => handleEmojiRemove(emoji.id)}
                    >
                      <CloseIcon sx={{ fontSize: 10 }} />
                    </IconButton>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        ))}
      </Box>
    );
  };

  return (
    <Box>
      <Typography variant="h6">Selected users and emojis</Typography>
      {selectedMembers.length > 0 ? (
        renderTeamMembersWithEmojis()
      ) : selectedEmojis.length > 0 ? (
        renderEmojis()
      ) : (
        <Typography variant="body2">No team members or emojis selected.</Typography>
      )}
    </Box>
  );
}

export default SlackConfiguration;
