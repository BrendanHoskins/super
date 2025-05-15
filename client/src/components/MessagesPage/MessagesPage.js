import React, { useEffect, useState } from 'react';
import { Typography, Box, Container, TextField } from '@mui/material';
import API from '../../api/api';
import MessageCard from './MessageCard';

const MessagesPage = () => {
  const [messages, setMessages] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const response = await API.get('/messages/get-messages');
        setMessages(response.data);
      } catch (error) {
        console.error('Error fetching messages:', error);
      }
    };

    fetchMessages();
  }, []);

  const filteredMessages = messages.filter(message =>
    message.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
          Messages
        </Typography>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search messages..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ 
            mb: 2, 
            ml: -20,
            mr: -20, // Add right margin to align with the card
            width: 'calc(100% + 322.5px)', // Increase width to compensate for margins
          }}
        />
        <Box sx={{ ml: -20 }}>
          {filteredMessages.map((message) => (
            <MessageCard key={message.id} message={message} />
          ))}
        </Box>
      </Box>
    </Container>
  );
};

export default MessagesPage;