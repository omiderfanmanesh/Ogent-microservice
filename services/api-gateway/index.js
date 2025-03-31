const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 8080;

// Service URLs from environment
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'http://auth-service:8000/api';
const AGENT_SERVICE_URL = process.env.AGENT_SERVICE_URL || 'http://agent-service:8001/api';
const SOCKET_SERVICE_URL = process.env.SOCKET_SERVICE_URL || 'http://socket-service:3002';
const COMMAND_SERVICE_URL = process.env.COMMAND_SERVICE_URL || 'http://command-execution:5000/api';

// Middleware
app.use(cors());
app.use(express.json());

// Simple request logger
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Auth service proxy
app.use('/auth', createProxyMiddleware({
  target: AUTH_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/auth': '',
  },
}));

// Agent service proxy (if available)
app.use('/agents', createProxyMiddleware({
  target: AGENT_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/agents': '',
  },
  onError: (err, req, res) => {
    console.error('Agent service proxy error:', err);
    res.status(503).json({ error: 'Agent service unavailable' });
  }
}));

// Command execution service proxy
app.use('/commands', createProxyMiddleware({
  target: COMMAND_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/commands': '',
  },
}));

// Socket service proxy for HTTP endpoints
app.use('/socket-http', createProxyMiddleware({
  target: SOCKET_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/socket-http': '',
  },
}));

// User endpoint - shorthand for auth service user endpoint
app.use('/user', createProxyMiddleware({
  target: `${AUTH_SERVICE_URL}/user`,
  changeOrigin: true,
  pathRewrite: {
    '^/user': '',
  },
}));

// Catch-all route
app.use('*', (req, res) => {
  res.status(404).json({ error: 'API endpoint not found' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ 
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Start server
app.listen(port, () => {
  console.log(`API Gateway running on port ${port}`);
}); 