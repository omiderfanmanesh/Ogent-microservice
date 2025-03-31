const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const axios = require('axios');

// Load environment variables
dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.FRONTEND_URL || "*",
    methods: ["GET", "POST"],
    credentials: true
  }
});

const PORT = process.env.PORT || 3002;
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'http://auth-service:8000/api';

// Store active execution sessions
const activeSessions = new Map();

// Middleware to verify JWT token
const authenticateSocket = async (socket, next) => {
  const token = socket.handshake.auth.token;
  
  if (!token) {
    return next(new Error('Authentication error: Token required'));
  }
  
  try {
    // Verify token with auth service
    const response = await axios.get(`${AUTH_SERVICE_URL}/user`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    
    if (response.status === 200) {
      socket.user = response.data.user;
      next();
    } else {
      next(new Error('Authentication error: Invalid token'));
    }
  } catch (error) {
    console.error('Token verification error:', error.message);
    next(new Error('Authentication error: Failed to verify token'));
  }
};

// Apply authentication middleware
io.use(authenticateSocket);

// Socket connection handler
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.user.id}`);
  
  // Join user to their own room
  socket.join(`user:${socket.user.id}`);
  
  // Handle execution monitoring
  socket.on('join-execution', (executionId) => {
    socket.join(`execution:${executionId}`);
    console.log(`${socket.user.id} joined execution: ${executionId}`);
    
    // Send initial session data if available
    const sessionData = activeSessions.get(executionId);
    if (sessionData) {
      socket.emit('execution-status', {
        executionId,
        status: sessionData.status,
        progress: sessionData.progress
      });
    }
  });
  
  socket.on('leave-execution', (executionId) => {
    socket.leave(`execution:${executionId}`);
    console.log(`${socket.user.id} left execution: ${executionId}`);
  });
  
  // Handle disconnect
  socket.on('disconnect', () => {
    console.log(`User disconnected: ${socket.user.id}`);
  });
});

// API endpoint to update execution status (from command execution service)
app.post('/api/execution-status', async (req, res) => {
  const { executionId, status, progress, output, error } = req.body;
  
  if (!executionId) {
    return res.status(400).json({ error: 'Execution ID is required' });
  }
  
  // Update active session data
  activeSessions.set(executionId, {
    status,
    progress,
    output,
    error,
    updatedAt: new Date()
  });
  
  // Emit to all clients monitoring this execution
  io.to(`execution:${executionId}`).emit('execution-status', {
    executionId,
    status,
    progress,
    output,
    error
  });
  
  res.status(200).json({ success: true });
});

// API endpoint to initiate execution (from agent service)
app.post('/api/start-execution', async (req, res) => {
  const { executionId, agent, input, userId } = req.body;
  
  if (!executionId || !agent || !userId) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  
  // Store initial session data
  activeSessions.set(executionId, {
    status: 'queued',
    progress: 0,
    createdAt: new Date()
  });
  
  // Notify user that execution is starting
  io.to(`user:${userId}`).emit('execution-started', {
    executionId,
    agent,
    input
  });
  
  res.status(200).json({ success: true });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Start server
server.listen(PORT, () => {
  console.log(`Socket service running on port ${PORT}`);
}); 