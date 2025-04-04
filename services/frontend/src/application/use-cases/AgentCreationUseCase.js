/**
 * Use case for creating a new agent
 */
export class AgentCreationUseCase {
  /**
   * Constructor
   * 
   * @param {Object} agentRepository - Repository for agent data access
   * @param {Function} getUserId - Function to get current user ID
   */
  constructor(agentRepository, getUserId) {
    this.agentRepository = agentRepository;
    this.getUserId = getUserId;
  }

  /**
   * Execute the use case
   * 
   * @param {Object} agentData - Agent data including name, type, and configuration
   * @returns {Promise<Object>} Created agent
   */
  async execute(agentData) {
    // Validate that we have required data
    if (!agentData.name || !agentData.type) {
      throw new Error('Agent name and type are required');
    }

    // Get the current user ID
    const userId = this.getUserId();
    if (!userId) {
      throw new Error('User must be authenticated to create an agent');
    }

    // Create the agent
    const agent = await this.agentRepository.create({
      ...agentData,
      userId,
      createdAt: new Date(),
      updatedAt: new Date()
    });

    return agent;
  }
} 