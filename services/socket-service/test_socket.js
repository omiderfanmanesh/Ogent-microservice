const axios = require('axios');

// URLs
const API_GATEWAY_URL = 'http://localhost:8081';
const SOCKET_SERVICE_DIRECT_URL = 'http://localhost:3002';

// Test the socket service health endpoint via API Gateway
const testSocketService = async () => {
  try {
    console.log('Testing Socket Service...');

    // Try direct access to socket service health endpoint via API Gateway
    console.log('\nTesting API Gateway proxy to Socket service:');
    try {
      const response = await axios.get(`${API_GATEWAY_URL}/socket-http/health`);
      console.log('✅ Socket service health via API Gateway:', response.data);
    } catch (error) {
      console.error('❌ Error accessing socket service via API Gateway:', error.message);
    }

    console.log('\nTest complete.');
  } catch (error) {
    console.error('Test failed with error:', error.message);
  }
};

// Run the test
testSocketService(); 