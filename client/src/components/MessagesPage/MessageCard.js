import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import { format } from 'date-fns';

const MessageCard = ({ message }) => {
  const { user, content, timestamp } = message;

  // Convert Slack timestamp to a readable format
  const date = new Date(parseFloat(timestamp) * 1000);
  const formattedDate = format(date, 'MMMM d, yyyy h:mm a');

  return (
    <Card sx={{ display: 'flex', alignItems: 'center', mb: 2, mr: -20, backgroundColor: '#f8fbff' }}>
      <img 
        src="/slack.svg" 
        alt="Slack logo" 
        style={{ width: '45px', height: '45px', marginRight: 16, marginLeft: 30 }} 
      />
      <CardContent>
        <Typography variant="subtitle1" color="textSecondary">
          {user}
        </Typography>
        <Typography variant="body1" gutterBottom>
          {content}
        </Typography>
        <Typography variant="caption" color="textSecondary">
          {formattedDate}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default MessageCard;
