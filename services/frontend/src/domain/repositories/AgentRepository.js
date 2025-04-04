/**
 * Repository interface for Agent entities.
 * This is an abstract interface that defines the contract for agent data access.
 * Implementations will be provided in the infrastructure layer.
 */
export class AgentRepository {
  /**
   * Get all agents for a user
   * @param {string} userId - User ID
   * @returns {Promise<Array>} Promise resolving to array of agents
   */
  async getAll(userId) {
    throw new Error('Method not implemented');
  }

  /**
   * Get agent by ID
   * @param {string} agentId - Agent ID
   * @param {string} userId - User ID for access control
   * @returns {Promise<Object>} Promise resolving to an agent
   */
  async getById(agentId, userId) {
    throw new Error('Method not implemented');
  }

  /**
   * Create a new agent
   * @param {Object} agentData - Agent data
   * @param {string} userId - User ID
   * @returns {Promise<Object>} Promise resolving to created agent
   */
  async create(agentData, userId) {
    throw new Error('Method not implemented');
  }

  /**
   * Update an agent
   * @param {string} agentId - Agent ID
   * @param {Object} agentData - Updated agent data
   * @param {string} userId - User ID for access control
   * @returns {Promise<Object>} Promise resolving to updated agent
   */
  async update(agentId, agentData, userId) {
    throw new Error('Method not implemented');
  }

  /**
   * Delete an agent
   * @param {string} agentId - Agent ID
   * @param {string} userId - User ID for access control
   * @returns {Promise<boolean>} Promise resolving to deletion success
   */
  async delete(agentId, userId) {
    throw new Error('Method not implemented');
  }

  /**
   * Execute an agent
   * @param {string} agentId - Agent ID
   * @param {Object} executionData - Execution parameters
   * @param {string} userId - User ID for access control
   * @returns {Promise<Object>} Promise resolving to execution details
   */
  async execute(agentId, executionData, userId) {
    throw new Error('Method not implemented');
  }
} 