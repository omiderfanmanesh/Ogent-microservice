import axios from 'axios';

const API_URL = process.env.REACT_APP_AUTH_URL || 'http://localhost:8080/auth';

const AuthService = {
  // Set up axios instance with token
  getAxiosInstance(token = null) {
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return axios.create({
      baseURL: API_URL,
      headers,
    });
  },

  // Register a new user
  async register(userData) {
    try {
      const response = await this.getAxiosInstance().post('/register', userData);
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Login user
  async login(credentials) {
    try {
      // Provide either email or username
      const response = await this.getAxiosInstance().post('/login', credentials);
      
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        return response.data;
      } else {
        throw new Error('No token received from server');
      }
    } catch (error) {
      this.handleError(error);
    }
  },

  // Logout a user
  async logout() {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        await this.getAxiosInstance(token).post('/logout');
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },

  // Get the current user's data
  async getCurrentUser() {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await this.getAxiosInstance(token).get('/user');
      return response.data.user;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  // Handle API errors
  handleError(error) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      if (error.response.status === 401) {
        // Unauthorized - clear stored data
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
      
      // Return error data from the server if available
      if (error.response.data) {
        return error.response.data;
      }
    }
    
    // For network errors or other issues
    return {
      message: error.message || 'An unexpected error occurred',
    };
  },
};

export default AuthService; 