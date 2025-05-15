import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Tabs,
  Tab,
  Checkbox,
  Avatar,
  Typography,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Chip,
} from '@mui/material';

function SlackTeam({
  usersByGroup,
  searchTerm,
  activeTab,
  onSearch,
  onTabClick,
  onMemberSelect,
  initialSelectedMembers,
}) {
  const groupNames = Object.keys(usersByGroup);
  const tabs = ['All', ...groupNames];

  // State to manage selected members (store full user objects)
  const [selectedMembers, setSelectedMembers] = useState({});

  useEffect(() => {
    if (initialSelectedMembers) {
      const initialSelected = {};
      initialSelectedMembers.forEach((member) => {
        initialSelected[member.id] = member;
      });
      setSelectedMembers(initialSelected);
    }
  }, [initialSelectedMembers]);

  // Filter users based on search term and active tab
  const getFilteredUsers = () => {
    const filteredUsers = {};

    groupNames.forEach((group) => {
      if (activeTab === 'All' || activeTab === group) {
        const users = usersByGroup[group].filter((user) => {
          const name = user.profile.real_name || user.name || '';
          return name.toLowerCase().includes(searchTerm.toLowerCase());
        });
        if (users.length > 0) {
          filteredUsers[group] = users;
        }
      }
    });

    return filteredUsers;
  };

  const filteredUsers = getFilteredUsers();

  // Handle checkbox toggle
  const handleCheckboxChange = (user) => {
    setSelectedMembers((prevSelected) => {
      const newSelected = { ...prevSelected };
      if (newSelected[user.id]) {
        delete newSelected[user.id];
      } else {
        newSelected[user.id] = user;
      }
      // Pass selected members up to parent component
      onMemberSelect(Object.values(newSelected));
      return newSelected;
    });
  };

  return (
    <Box>
      {/* Search Bar */}
      <TextField
        variant="outlined"
        placeholder="Search team members"
        value={searchTerm}
        onChange={onSearch}
        fullWidth
        margin="dense"
      />

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onChange={(e, value) => onTabClick(value)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ marginBottom: 2 }}
      >
        {tabs.map((tabName, index) => (
          <Tab key={index} label={tabName} value={tabName} />
        ))}
      </Tabs>

      {/* Users List */}
      <Box
        sx={{
          maxHeight: '400px',
          overflowY: 'auto',
          border: '1px solid #ddd',
          padding: 1,
          borderRadius: 1,
        }}
      >
        {Object.keys(filteredUsers).length === 0 && <Typography>No team members found.</Typography>}
        {Object.keys(filteredUsers).map((group) => (
          <Box key={group} sx={{ marginBottom: 2 }}>
            {activeTab === 'All' && <Typography variant="subtitle1">{group}</Typography>}
            <List>
              {filteredUsers[group].map((user) => (
                <ListItem key={user.id} disableGutters>
                  <Checkbox
                    checked={!!selectedMembers[user.id]}
                    onChange={() => handleCheckboxChange(user)}
                  />
                  <ListItemAvatar>
                    <Avatar src={user.profile.image_32 || user.profile.image_72} />
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography>{user.profile.real_name || user.name}</Typography>
                        {user.is_bot && (
                          <Chip
                            label="Bot"
                            size="small"
                            sx={{
                              ml: 1,
                              backgroundColor: 'rgba(0, 0, 0, 0.08)',
                              color: 'rgba(0, 0, 0, 0.6)',
                              height: '20px',
                            }}
                          />
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        ))}
      </Box>
    </Box>
  );
}

export default SlackTeam;
