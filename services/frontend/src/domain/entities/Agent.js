/**
 * Agent entity representing an AI agent in the system.
 */
export class Agent {
  /**
   * @param {string} id - Unique identifier
   * @param {string} name - Agent name
   * @param {string} type - Agent type (e.g., "conversational", "command")
   * @param {Object} configuration - Agent configuration
   * @param {Object} permissions - Agent permissions
   * @param {string} ownerId - ID of user owning the agent
   * @param {Date} createdAt - Creation date
   * @param {Date} updatedAt - Last update date
   */
  constructor(
    id,
    name,
    type,
    configuration = {},
    permissions = {},
    ownerId,
    createdAt = new Date(),
    updatedAt = new Date()
  ) {
    this.id = id;
    this.name = name;
    this.type = type;
    this.configuration = configuration;
    this.permissions = permissions;
    this.ownerId = ownerId;
    this.createdAt = createdAt instanceof Date ? createdAt : new Date(createdAt);
    this.updatedAt = updatedAt instanceof Date ? updatedAt : new Date(updatedAt);
  }

  /**
   * Check if agent has specific permission
   * @param {string} permission - Permission to check
   * @returns {boolean} Whether agent has the permission
   */
  hasPermission(permission) {
    return Boolean(this.permissions[permission]);
  }

  /**
   * Update agent configuration
   * @param {Object} config - New configuration
   */
  updateConfiguration(config) {
    this.configuration = { ...this.configuration, ...config };
    this.updatedAt = new Date();
  }

  /**
   * Create agent from API response
   * @param {Object} data - API response data
   * @returns {Agent} Agent entity
   */
  static fromApiResponse(data) {
    return new Agent(
      data.id,
      data.name,
      data.type,
      data.configuration || {},
      data.permissions || {},
      data.owner_id,
      data.created_at,
      data.updated_at
    );
  }
} 