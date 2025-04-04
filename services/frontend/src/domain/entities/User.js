/**
 * User entity representing a user in the system.
 */
export class User {
  /**
   * @param {string} id - Unique identifier
   * @param {string} username - Username
   * @param {string} email - Email address
   * @param {string[]} roles - User roles
   * @param {Object} profile - Additional profile information
   */
  constructor(id, username, email, roles = [], profile = {}) {
    this.id = id;
    this.username = username;
    this.email = email;
    this.roles = roles;
    this.profile = profile;
    this.isAuthenticated = false;
    this.lastLoginAt = null;
  }

  /**
   * Check if user has specific role
   * @param {string} role - Role to check
   * @returns {boolean} Whether user has the role
   */
  hasRole(role) {
    return this.roles.includes(role);
  }

  /**
   * Set authenticated status and update last login time
   * @param {boolean} status - Authentication status
   */
  setAuthenticated(status) {
    this.isAuthenticated = status;
    
    if (status) {
      this.lastLoginAt = new Date();
    }
  }

  /**
   * Create user from API response
   * @param {Object} data - API response data
   * @returns {User} User entity
   */
  static fromApiResponse(data) {
    const user = new User(
      data.id,
      data.username,
      data.email,
      data.roles || [],
      data.profile || {}
    );
    
    if (data.is_authenticated) {
      user.setAuthenticated(true);
    }
    
    return user;
  }
} 