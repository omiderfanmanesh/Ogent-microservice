/**
 * HTTP-based implementation of the Agent Repository
 */
export class HttpAgentRepository {
  /**
   * Constructor
   * 
   * @param {string} baseUrl - Base URL for the API
   */
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  /**
   * Get authenticated request options
   * 
   * @param {Object} options - Additional request options
   * @returns {Object} Request options with auth headers
   */
  getAuthHeaders(options = {}) {
    const token = localStorage.getItem('auth_token');
    
    return {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    };
  }

  /**
   * Get all agents for a user
   * 
   * @param {string} userId - User ID
   * @returns {Promise<Array>} List of agents
   */
  async getAll(userId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/agents`, 
        this.getAuthHeaders());
      
      if (!response.ok) {
        throw new Error(`Failed to fetch agents: ${response.status}`);
      }
      
      const data = await response.json();
      return data.agents || [];
    } catch (error) {
      console.error('Error fetching agents:', error);
      throw error;
    }
  }

  /**
   * Get agent by ID
   * 
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Agent data
   */
  async getById(agentId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/agents/${agentId}`,
        this.getAuthHeaders());
      
      if (!response.ok) {
        throw new Error(`Failed to fetch agent: ${response.status}`);
      }
      
      const data = await response.json();
      return data.agent;
    } catch (error) {
      console.error(`Error fetching agent ${agentId}:`, error);
      throw error;
    }
  }

  /**
   * Create a new agent
   * 
   * @param {Object} agentData - Agent data
   * @returns {Promise<Object>} Created agent
   */
  async create(agentData) {
    try {
      const response = await fetch(`${this.baseUrl}/api/agents`, 
        this.getAuthHeaders({
          method: 'POST',
          body: JSON.stringify(agentData)
        }));
      
      if (!response.ok) {
        throw new Error(`Failed to create agent: ${response.status}`);
      }
      
      const data = await response.json();
      return data.agent;
    } catch (error) {
      console.error('Error creating agent:', error);
      throw error;
    }
  }

  /**
   * Update an existing agent
   * 
   * @param {string} agentId - Agent ID
   * @param {Object} agentData - Updated agent data
   * @returns {Promise<Object>} Updated agent
   */
  async update(agentId, agentData) {
    try {
      const response = await fetch(`${this.baseUrl}/api/agents/${agentId}`,
        this.getAuthHeaders({
          method: 'PUT',
          body: JSON.stringify(agentData)
        }));
      
      if (!response.ok) {
        throw new Error(`Failed to update agent: ${response.status}`);
      }
      
      const data = await response.json();
      return data.agent;
    } catch (error) {
      console.error(`Error updating agent ${agentId}:`, error);
      throw error;
    }
  }

  /**
   * Delete an agent
   * 
   * @param {string} agentId - Agent ID
   * @returns {Promise<boolean>} Success status
   */
  async delete(agentId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/agents/${agentId}`,
        this.getAuthHeaders({
          method: 'DELETE'
        }));
      
      if (!response.ok) {
        throw new Error(`Failed to delete agent: ${response.status}`);
      }
      
      return true;
    } catch (error) {
      console.error(`Error deleting agent ${agentId}:`, error);
      throw error;
    }
  }

  /**
   * Execute an agent
   * 
   * @param {string} agentId - Agent ID
   * @param {Object} executionData - Execution parameters
   * @returns {Promise<Object>} Execution result
   */
  async execute(agentId, executionData) {
    try {
      const response = await fetch(`${this.baseUrl}/api/agents/${agentId}/execute`,
        this.getAuthHeaders({
          method: 'POST',
          body: JSON.stringify(executionData)
        }));
      
      if (!response.ok) {
        throw new Error(`Failed to execute agent: ${response.status}`);
      }
      
      const data = await response.json();
      return data.result;
    } catch (error) {
      console.error(`Error executing agent ${agentId}:`, error);
      throw error;
    }
  }
} 