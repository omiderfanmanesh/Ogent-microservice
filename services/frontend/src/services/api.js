import axios from 'axios';

// Create an axios instance with base URL
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add a request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // Handle session expiration
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Only redirect to login if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error.response?.data || error);
  }
);

// Auth endpoints
const auth = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  me: () => api.get('/auth/me'),
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return Promise.resolve();
  }
};

// Agent endpoints
const agents = {
  list: (params = {}) => api.get('/agents', { params }),
  getById: (id) => api.get(`/agents/${id}`),
  create: (agentData) => api.post('/agents', agentData),
  update: (id, agentData) => api.put(`/agents/${id}`, agentData),
  delete: (id) => api.delete(`/agents/${id}`),
  getTypes: () => api.get('/agents/types')
};

// Execution endpoints
const executions = {
  list: (params = {}) => api.get('/executions', { params }),
  getById: (id) => api.get(`/executions/${id}`),
  create: (agentId, executionData) => api.post(`/agents/${agentId}/executions`, executionData),
  getSteps: (executionId) => api.get(`/executions/${executionId}/steps`),
  getCommands: (executionId, stepId) => api.get(`/executions/${executionId}/steps/${stepId}/commands`),
  delete: (id) => api.delete(`/executions/${id}`)
};

// Stats endpoints
const stats = {
  dashboard: () => api.get('/stats/dashboard')
};

// Combine all services
const apiService = {
  auth,
  agents,
  executions,
  stats
};

export default apiService; 