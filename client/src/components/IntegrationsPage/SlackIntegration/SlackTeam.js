import React, { useState, useEffect } from 'react';

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
    <div>
      {/* Search Bar */}
      <input
        type="text"
        placeholder="Search team members"
        value={searchTerm}
        onChange={onSearch}
        style={{ marginBottom: '10px', width: '100%', padding: '8px' }}
      />

      {/* Tabs */}
      <div style={{ marginBottom: '10px' }}>
        {tabs.map((tabName, index) => (
          <button
            key={index}
            onClick={() => onTabClick(tabName)}
            style={{
              marginRight: '5px',
              padding: '8px 12px',
              backgroundColor: activeTab === tabName ? '#0078d4' : '#e5e5e5',
              color: activeTab === tabName ? 'white' : 'black',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            {tabName}
          </button>
        ))}
      </div>

      {/* Users List */}
      <div
        style={{
          maxHeight: '400px',
          overflowY: 'auto',
          border: '1px solid #ddd',
          padding: '10px',
          borderRadius: '4px',
        }}
      >
        {Object.keys(filteredUsers).length === 0 && <p>No team members found.</p>}
        {Object.keys(filteredUsers).map((group) => (
          <div key={group} style={{ marginBottom: '20px' }}>
            {activeTab === 'All' && <h3>{group}</h3>}
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {filteredUsers[group].map((user) => (
                <li
                  key={user.id}
                  style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}
                >
                  <input
                    type="checkbox"
                    checked={!!selectedMembers[user.id]}
                    onChange={() => handleCheckboxChange(user)}
                    style={{ marginRight: '10px' }}
                  />
                  <img
                    src={user.profile.image_32 || user.profile.image_72}
                    alt={user.profile.real_name || user.name}
                    style={{ marginRight: '10px', borderRadius: '50%' }}
                  />
                  <span style={{ marginRight: '10px' }}>
                    {user.profile.real_name || user.name}
                  </span>
                  {user.is_bot && (
                    <span
                      style={{
                        backgroundColor: '#f0f0f0',
                        color: '#666',
                        padding: '2px 6px',
                        borderRadius: '10px',
                        fontSize: '0.8em',
                      }}
                    >
                      Bot
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Selected Team Members */}
      <div style={{ marginTop: '20px' }}>
        <h3>Selected Team Members:</h3>
        {Object.values(selectedMembers).length === 0 ? (
          <p>No team members selected.</p>
        ) : (
          <ul style={{ listStyleType: 'none', padding: 0 }}>
            {Object.values(selectedMembers).map((member) => (
              <li
                key={member.id}
                style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}
              >
                <img
                  src={member.profile.image_32 || member.profile.image_72}
                  alt={member.profile.real_name || member.name}
                  style={{ marginRight: '10px', borderRadius: '50%' }}
                />
                <span style={{ marginRight: '10px' }}>
                  {member.profile.real_name || member.name}
                </span>
                {member.is_bot && (
                  <span
                    style={{
                      backgroundColor: '#f0f0f0',
                      color: '#666',
                      padding: '2px 6px',
                      borderRadius: '10px',
                      fontSize: '0.8em',
                    }}
                  >
                    Bot
                  </span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default SlackTeam;