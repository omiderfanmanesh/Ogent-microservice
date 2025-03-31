import axios from 'axios';

const API_URL = process.env.REACT_APP_COMMAND_SERVICE_URL || 'http://localhost:5000';

class CommandService {
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
  }

  // Execute a command
  async executeCommand(command, token) {
    try {
      const response = await this.getAxiosInstance(token).post('/api/execute', { command });
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  // Get execution status
  async getExecutionStatus(executionId, token) {
    try {
      const response = await this.getAxiosInstance(token).get(`/api/execution/${executionId}`);
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  // Cancel execution
  async cancelExecution(executionId, token) {
    try {
      const response = await this.getAxiosInstance(token).post(`/api/execution/${executionId}/cancel`);
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  // Handle API errors
  handleError(error) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      const errorData = error.response.data;
      throw {
        status: error.response.status,
        message: errorData.error || errorData.message || 'An error occurred',
        data: errorData
      };
    } else if (error.request) {
      // The request was made but no response was received
      throw {
        status: 0,
        message: 'No response from server',
        data: error.request
      };
    } else {
      // Something happened in setting up the request that triggered an Error
      throw {
        status: 0,
        message: error.message || 'An unexpected error occurred',
        data: error
      };
    }
  }
}

// Create a singleton instance
const commandService = new CommandService();

export default commandService; 