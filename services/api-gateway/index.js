const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');
const dotenv = require('dotenv');
const fetch = require('node-fetch');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 8081; // Changed default port to 8081

// Service URLs from environment
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'http://auth-service:80/api';
const AGENT_SERVICE_URL = process.env.AGENT_SERVICE_URL || 'http://agent-service:8000/api';
const SOCKET_SERVICE_URL = process.env.SOCKET_SERVICE_URL || 'http://socket-service:3002';
const COMMAND_SERVICE_URL = process.env.COMMAND_SERVICE_URL || 'http://command-execution:5000/api';

// Middleware
app.use(cors({
  origin: process.env.ALLOW_ORIGINS ? process.env.ALLOW_ORIGINS.split(',') : '*',
  credentials: true
}));
app.use(express.json());

// Simple request logger
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Simplified Auth API login endpoint
app.post('/api/login', (req, res) => {
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(req.body),
    timeout: 5000
  };
  
  console.log(`Forwarding login request to: ${AUTH_SERVICE_URL}/login`);
  
  fetch(`http://auth-service:80/api/login`, options)
    .then(response => {
      if (!response.ok) {
        throw new Error(`Auth service responded with status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Login successful');
      res.json(data);
    })
    .catch(error => {
      console.error('Login error:', error);
      res.status(500).json({ 
        message: 'Authentication service error', 
        error: error.message 
      });
    });
});

// Auth api proxy middleware for other auth endpoints
const authApiProxy = createProxyMiddleware({
  target: 'http://auth-service:80',
  changeOrigin: true,
  pathRewrite: {
    '^/api/register': '/api/register',
    '^/api/logout': '/api/logout',
    '^/api/verify': '/api/verify',
    '^/api/user': '/api/user',
    '^/api/debug': '/api/debug',
  },
  onError: (err, req, res) => {
    console.error(`[Auth Service Error]: ${err.message}`);
    console.error(err.stack);
    res.status(500).json({ message: 'Auth Service Unavailable', error: err.message });
  },
  logLevel: 'debug',
  timeout: 30000, // 30 second timeout
  proxyTimeout: 30000,
});

// Agent service proxy middleware
const agentServiceProxy = createProxyMiddleware({
  target: AGENT_SERVICE_URL.replace('/api', ''),
  changeOrigin: true,
  pathRewrite: {
    '^/agents': '/api'
  },
  onError: (err, req, res) => {
    console.error(`[Agent Service Error]: ${err.message}`);
    res.status(500).json({ message: 'Agent Service Unavailable', error: err.message });
  },
  timeout: 30000,
});

// Command execution proxy middleware
const commandServiceProxy = createProxyMiddleware({
  target: COMMAND_SERVICE_URL.replace('/api', ''),
  changeOrigin: true,
  pathRewrite: {
    '^/commands': '/api'
  },
  onError: (err, req, res) => {
    console.error(`[Command Service Error]: ${err.message}`);
    res.status(500).json({ message: 'Command Service Unavailable', error: err.message });
  },
  timeout: 120000, // 2 minute timeout for commands
});

// Socket service proxy middleware
const socketServiceProxy = createProxyMiddleware({
  target: SOCKET_SERVICE_URL,
  changeOrigin: true,
  ws: true,
  pathRewrite: {
    '^/socket-http': ''
  },
  onError: (err, req, res) => {
    console.error(`[Socket Service Error]: ${err.message}`);
    res.status(500).json({ message: 'Socket Service Unavailable', error: err.message });
  },
  timeout: 30000,
});

// User proxy middleware
const userProxy = createProxyMiddleware({
  target: AUTH_SERVICE_URL.replace('/api', ''),
  changeOrigin: true,
  pathRewrite: {
    '^/user': '/api/user'
  },
  onError: (err, req, res) => {
    console.error(`[User Service Error]: ${err.message}`);
    res.status(500).json({ message: 'User Service Unavailable', error: err.message });
  },
  timeout: 30000,
});

// Routes
// Log all incoming requests
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Auth routes (except login which is handled directly)
app.use('/api/register', authApiProxy);
app.use('/api/logout', authApiProxy);
app.use('/api/verify', authApiProxy);
app.use('/auth', authApiProxy); // Backwards compatibility for /auth routes

// Service routes
app.use('/agents', agentServiceProxy);
app.use('/commands', commandServiceProxy);
app.use('/socket-http', socketServiceProxy);
app.use('/user', userProxy);

// Default route for unmatched requests
app.use((req, res) => {
  res.status(404).json({ message: 'API endpoint not found' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(`[Server Error]: ${err.message}`);
  console.error(err.stack);
  res.status(500).json({ message: 'Internal Server Error', error: err.message });
});

// Start the server
app.listen(PORT, () => {
  console.log(`API Gateway is running on port ${PORT}`);
});