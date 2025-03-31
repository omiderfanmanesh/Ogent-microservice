import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const RoleList = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Role Management
      </Typography>
      
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Role management interface will be implemented here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default RoleList; 