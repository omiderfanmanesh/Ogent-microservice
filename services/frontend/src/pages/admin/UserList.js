import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const UserList = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        User Management
      </Typography>
      
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          User management interface will be implemented here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default UserList; 