const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');

const app = express();
const port = 3000;

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

// Agent service proxy (direct with IP)
app.use('/direct', createProxyMiddleware({
  target: 'http://172.18.0.7:8000',
  changeOrigin: true,
  onError: (err, req, res) => {
    console.error('Direct proxy error:', err);
    res.status(503).json({ error: 'Direct proxy unavailable' });
  }
}));

// Start server
app.listen(port, () => {
  console.log(`Debug server running on port ${port}`);
}); 