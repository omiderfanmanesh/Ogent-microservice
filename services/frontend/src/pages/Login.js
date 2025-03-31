import React from 'react';
import { Container, Box, Typography } from '@mui/material';
import LoginForm from '../components/auth/LoginForm';

const Login = () => {
  return (
    <Container maxWidth="sm">
      <Box sx={{ my: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Ogent Platform
        </Typography>
        <LoginForm />
      </Box>
    </Container>
  );
};

export default Login; 