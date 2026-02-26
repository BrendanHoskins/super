import React, { useEffect, useState, useRef } from 'react';
import { Typography, Box, Container, TextField } from '@mui/material';
import API from '../../api/api';
import { getAccessToken } from '../../services/AuthService';
import MessageCard from './MessageCard';

const MessagesPage = () => {
  const [messages, setMessages] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const eventSourceRef = useRef(null);

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

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;

    const baseURL = import.meta.env.VITE_BACKEND_URL?.replace(/\/$/, '') || '';
    const url = `${baseURL}/messages/stream?access_token=${encodeURIComponent(token)}`;
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.addEventListener('message_created', (event) => {
      try {
        const message = JSON.parse(event.data);
        setMessages((prev) => [message, ...prev]);
      } catch (e) {
        console.error('SSE message_created parse error:', e);
      }
    });

    eventSource.addEventListener('message_updated', (event) => {
      try {
        const updated = JSON.parse(event.data);
        setMessages((prev) =>
          prev.map((m) => (m.id === updated.id ? updated : m))
        );
      } catch (e) {
        console.error('SSE message_updated parse error:', e);
      }
    });

    eventSource.addEventListener('message_removed', (event) => {
      try {
        const removed = JSON.parse(event.data);
        setMessages((prev) => prev.filter((m) => m.id !== removed.id));
      } catch (e) {
        console.error('SSE message_removed parse error:', e);
      }
    });

    eventSource.onerror = (err) => {
      console.error('Messages SSE error:', err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
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