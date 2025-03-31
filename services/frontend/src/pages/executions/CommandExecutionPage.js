import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Alert, 
  Breadcrumbs, 
  Link 
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import CommandExecutor from '../../components/execution/CommandExecutor';

const CommandExecutionPage = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link component={RouterLink} to="/dashboard" underline="hover" color="inherit">
          Dashboard
        </Link>
        <Link component={RouterLink} to="/executions" underline="hover" color="inherit">
          Executions
        </Link>
        <Typography color="text.primary">Command Execution</Typography>
      </Breadcrumbs>
      
      <Typography variant="h4" component="h1" gutterBottom>
        Command Execution
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        This page allows you to execute commands on the target machine. Only allowed commands
        will be executed. Commands are run in a secure environment with limited permissions.
      </Alert>
      
      <Paper sx={{ p: 3 }}>
        <CommandExecutor />
      </Paper>
    </Box>
  );
};

export default CommandExecutionPage; 