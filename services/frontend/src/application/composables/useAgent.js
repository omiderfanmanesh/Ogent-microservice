import { ref, computed } from 'vue';

/**
 * Utility function to get authenticated request options
 * 
 * @param {Object} options - Request options
 * @returns {Object} Request options with auth headers
 */
const getAuthRequestOptions = (options = {}) => {
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
};

/**
 * Composable for agent management.
 * Provides reactive state and methods for working with agents.
 * 
 * @param {AgentRepository} agentRepository - Repository for agent data access
 * @param {function} getUserId - Function to get current user ID
 * @returns {Object} Agent management utilities and state
 */
export function useAgent(agentRepository, getUserId) {
  const agents = ref([
    {
      id: '1',
      name: 'General Assistant',
      type: 'conversational',
      description: 'A general purpose AI assistant',
      createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
      permissions: { canSendEmail: true, canAccessFiles: false }
    },
    {
      id: '2',
      name: 'Command Runner',
      type: 'command',
      description: 'Executes shell commands',
      createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
      updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
      permissions: { canExecuteCommands: true, canAccessFiles: true }
    },
    {
      id: '3',
      name: 'Function Bot',
      type: 'function',
      description: 'Calls API functions',
      createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
      updatedAt: new Date(Date.now() - 12 * 60 * 60 * 1000),
      permissions: { canCallApi: true, canAccessDatabase: false }
    }
  ]);
  
  const currentAgent = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const hasAgents = computed(() => agents.value.length > 0);
  
  // We're using mock data so we don't need the use case instance
  // const agentCreationUseCase = new AgentCreationUseCase(agentRepository, getUserId);
  
  /**
   * Load agents for the current user
   */
  const loadAgents = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      // In a real app, this would call the repository
      // const userId = getUserId();
      // const loadedAgents = await agentRepository.getAll(userId);
      // agents.value = loadedAgents;
      
      // Just using the mock data above
      console.log('Loaded mock agents:', agents.value);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300));
    } catch (err) {
      console.error('Error loading agents:', err);
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Get a specific agent by ID
   * 
   * @param {string} agentId - Agent ID
   */
  const getAgent = async (agentId) => {
    loading.value = true;
    error.value = null;
    
    try {
      // In a real app, would use repository
      // const agent = await agentRepository.getById(agentId);
      
      // Using mock data
      const agent = agents.value.find(a => a.id === agentId);
      
      if (!agent) {
        throw new Error(`Agent with ID ${agentId} not found`);
      }
      
      currentAgent.value = agent;
      await new Promise(resolve => setTimeout(resolve, 200));
      
      return agent;
    } catch (err) {
      console.error(`Error getting agent ${agentId}:`, err);
      error.value = err.message;
      return null;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Create a new agent
   * 
   * @param {Object} agentData - Agent data
   */
  const createAgent = async (agentData) => {
    loading.value = true;
    error.value = null;
    
    try {
      // In a real app: await agentRepository.create(agentData);
      
      // Create a mock new agent
      const newAgent = {
        id: `${agents.value.length + 1}`,
        ...agentData,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      agents.value.push(newAgent);
      await new Promise(resolve => setTimeout(resolve, 300));
      
      return newAgent;
    } catch (err) {
      console.error('Error creating agent:', err);
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Update an existing agent
   * 
   * @param {string} agentId - Agent ID
   * @param {Object} agentData - Updated agent data
   */
  const updateAgent = async (agentId, agentData) => {
    loading.value = true;
    error.value = null;
    
    try {
      // In a real app: await agentRepository.update(agentId, agentData);
      
      // Update mock agent
      const index = agents.value.findIndex(a => a.id === agentId);
      
      if (index === -1) {
        throw new Error(`Agent with ID ${agentId} not found`);
      }
      
      const updatedAgent = {
        ...agents.value[index],
        ...agentData,
        updatedAt: new Date()
      };
      
      agents.value[index] = updatedAgent;
      
      if (currentAgent.value && currentAgent.value.id === agentId) {
        currentAgent.value = updatedAgent;
      }
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      return updatedAgent;
    } catch (err) {
      console.error(`Error updating agent ${agentId}:`, err);
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Delete an agent
   * 
   * @param {string} agentId - Agent ID to delete
   */
  const deleteAgent = async (agentId) => {
    loading.value = true;
    error.value = null;
    
    try {
      // In a real app: await agentRepository.delete(agentId);
      
      // Delete from mock agents
      const index = agents.value.findIndex(a => a.id === agentId);
      
      if (index === -1) {
        throw new Error(`Agent with ID ${agentId} not found`);
      }
      
      agents.value.splice(index, 1);
      
      if (currentAgent.value && currentAgent.value.id === agentId) {
        currentAgent.value = null;
      }
      
      await new Promise(resolve => setTimeout(resolve, 300));
    } catch (err) {
      console.error(`Error deleting agent ${agentId}:`, err);
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Execute an agent
   * 
   * @param {string} agentId - Agent ID to execute
   * @param {Object} executionData - Execution parameters
   */
  const executeAgent = async (agentId, executionData) => {
    console.log(`Executing agent ${agentId} with:`, executionData);
    
    // Find the agent
    const agent = agents.value.find(a => a.id === agentId);
    
    if (!agent) {
      throw new Error(`Agent with ID ${agentId} not found`);
    }
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Generate mock response based on agent type
    let output = '';
    
    if (agent.type === 'conversational') {
      output = `I'm ${agent.name}, a conversational AI. You said: "${executionData.input}"`;
      
      if (executionData.input.toLowerCase().includes('hello')) {
        output = `Hello! I'm ${agent.name}, an AI assistant. How can I help you today?`;
      } else if (executionData.input.toLowerCase().includes('help')) {
        output = `I'm here to assist you with information and tasks. What would you like to know?`;
      } else if (executionData.input.toLowerCase().includes('weather')) {
        output = `The weather today is sunny with a high of 75°F. Perfect day to go outside!`;
      } else if (executionData.input.endsWith('?')) {
        output = `That's an interesting question! As a conversational AI, I can provide information on a wide range of topics.`;
      }
    } else if (agent.type === 'command') {
      output = `Command executed: "${executionData.input}"\nOutput: This is a simulated command output.`;
    } else if (agent.type === 'function') {
      output = `Function called with input: "${executionData.input}"\nResult: { "status": "success", "data": { "processed": true } }`;
    }
    
    return {
      id: `exec_${Date.now()}`,
      agentId,
      input: executionData.input,
      output,
      status: 'completed',
      createdAt: new Date(),
      completedAt: new Date()
    };
  };
  
  // Return composable API
  return {
    // State
    agents,
    currentAgent,
    loading,
    error,
    
    // Computed
    hasAgents,
    
    // Methods
    loadAgents,
    getAgent,
    createAgent,
    updateAgent,
    deleteAgent,
    executeAgent
  };
} 