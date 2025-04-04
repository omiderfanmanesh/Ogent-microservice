import { HttpAgentRepository } from './api/HttpAgentRepository';
import { useUser } from '../application/composables/useUser';

/**
 * Factory to create application repositories and services
 */
export const createRepositories = () => {
  // Initialize services
  const { getUserId } = useUser();
  
  // Create repositories
  const agentRepository = new HttpAgentRepository('');
  
  return {
    agentRepository,
    getUserId
  };
}; 