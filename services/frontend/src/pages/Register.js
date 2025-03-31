import React from 'react';
import { Container, Box, Typography } from '@mui/material';
import RegisterForm from '../components/auth/RegisterForm';

const Register = () => {
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          mt: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}
      >
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ fontWeight: 'bold' }}
        >
          Ogent
        </Typography>
        <RegisterForm />
      </Box>
    </Container>
  );
};

export default Register; 