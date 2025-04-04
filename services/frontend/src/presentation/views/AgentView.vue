<template>
  <div class="agent-view">
    <h1>Your Agents</h1>
    
    <div v-if="loading" class="loading-state">
      <p>Loading agents...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <h3>Error loading agents</h3>
      <p>{{ error }}</p>
      <button @click="loadAgents" class="retry-button">Retry</button>
    </div>
    
    <div v-else class="agent-list-container">
      <div v-if="agents.length === 0" class="no-agents">
        <p>You don't have any agents yet.</p>
        <button @click="showCreateAgentModal = true" class="create-agent-button">
          Create your first agent
        </button>
      </div>
      
      <div v-else class="agents-grid">
        <div class="agent-controls">
          <button @click="showCreateAgentModal = true" class="create-agent-button">
            Create New Agent
          </button>
        </div>
        
        <div class="agent-cards">
          <div 
            v-for="agent in agents" 
            :key="agent.id" 
            class="agent-card"
            @click="selectAgent(agent.id)"
          >
            <div class="agent-card-header">
              <h3>{{ agent.name }}</h3>
              <span class="agent-type">{{ agent.type }}</span>
            </div>
            
            <p class="agent-description">{{ agent.description }}</p>
            
            <div class="agent-card-footer">
              <span class="agent-updated">
                Updated: {{ formatDate(agent.updatedAt) }}
              </span>
              <div class="agent-actions">
                <button @click.stop="prepareAgentForChat(agent)" class="chat-button">
                  Chat
                </button>
                <button @click.stop="editAgent(agent)" class="edit-button">
                  Edit
                </button>
                <button @click.stop="deleteAgentWithConfirm(agent.id)" class="delete-button">
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Agent Detail Modal -->
    <div v-if="selectedAgent" class="modal agent-detail-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ selectedAgent.name }}</h2>
          <button @click="selectedAgent = null" class="close-button">&times;</button>
        </div>
        <div class="modal-body">
          <div class="agent-detail-section">
            <h3>Details</h3>
            <div class="agent-detail-item">
              <strong>Type:</strong> {{ selectedAgent.type }}
            </div>
            <div class="agent-detail-item">
              <strong>Description:</strong> {{ selectedAgent.description }}
            </div>
            <div class="agent-detail-item">
              <strong>Created:</strong> {{ formatDate(selectedAgent.createdAt) }}
            </div>
            <div class="agent-detail-item">
              <strong>Last Updated:</strong> {{ formatDate(selectedAgent.updatedAt) }}
            </div>
          </div>
          
          <div class="agent-detail-section">
            <h3>Permissions</h3>
            <div v-if="selectedAgent.permissions" class="permissions-list">
              <div v-for="(value, key) in selectedAgent.permissions" :key="key" class="permission-item">
                <span class="permission-name">{{ formatPermissionName(key) }}:</span>
                <span class="permission-value" :class="{ 'enabled': value, 'disabled': !value }">
                  {{ value ? 'Enabled' : 'Disabled' }}
                </span>
              </div>
            </div>
            <div v-else class="no-permissions">
              No specific permissions set
            </div>
          </div>
          
          <div class="agent-actions-footer">
            <button @click="prepareAgentForChat(selectedAgent)" class="chat-button">
              Chat with this agent
            </button>
            <button @click="editAgent(selectedAgent)" class="edit-button">
              Edit this agent
            </button>
            <button @click="deleteAgentWithConfirm(selectedAgent.id)" class="delete-button">
              Delete this agent
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Agent Modal -->
    <div v-if="showCreateAgentModal || agentToEdit" class="modal create-agent-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ agentToEdit ? 'Edit Agent' : 'Create New Agent' }}</h2>
          <button @click="cancelAgentForm" class="close-button">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitAgentForm" class="agent-form">
            <div class="form-group">
              <label for="agent-name">Name</label>
              <input 
                id="agent-name" 
                v-model="agentForm.name" 
                type="text" 
                required
                placeholder="Enter agent name"
              />
            </div>
            
            <div class="form-group">
              <label for="agent-type">Type</label>
              <select 
                id="agent-type" 
                v-model="agentForm.type" 
                required
              >
                <option value="conversational">Conversational</option>
                <option value="command">Command</option>
                <option value="function">Function</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="agent-description">Description</label>
              <textarea 
                id="agent-description" 
                v-model="agentForm.description" 
                rows="3"
                placeholder="Describe what this agent does"
              ></textarea>
            </div>
            
            <div class="form-group permissions-section">
              <label>Permissions</label>
              <div class="permissions-checkboxes">
                <div class="permission-checkbox" v-if="agentForm.type === 'conversational'">
                  <input 
                    id="perm-send-email" 
                    type="checkbox" 
                    v-model="agentForm.permissions.canSendEmail"
                  />
                  <label for="perm-send-email">Can send emails</label>
                </div>
                
                <div class="permission-checkbox" v-if="agentForm.type === 'command'">
                  <input 
                    id="perm-execute-commands" 
                    type="checkbox" 
                    v-model="agentForm.permissions.canExecuteCommands"
                  />
                  <label for="perm-execute-commands">Can execute commands</label>
                </div>
                
                <div class="permission-checkbox">
                  <input 
                    id="perm-access-files" 
                    type="checkbox" 
                    v-model="agentForm.permissions.canAccessFiles"
                  />
                  <label for="perm-access-files">Can access files</label>
                </div>
                
                <div class="permission-checkbox" v-if="agentForm.type === 'function'">
                  <input 
                    id="perm-call-api" 
                    type="checkbox" 
                    v-model="agentForm.permissions.canCallApi"
                  />
                  <label for="perm-call-api">Can call APIs</label>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="cancelAgentForm" class="cancel-button">
                Cancel
              </button>
              <button type="submit" class="submit-button">
                {{ agentToEdit ? 'Update Agent' : 'Create Agent' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirmation" class="modal delete-confirm-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Confirm Deletion</h2>
          <button @click="showDeleteConfirmation = false" class="close-button">&times;</button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete this agent? This action cannot be undone.</p>
          <div class="modal-actions">
            <button @click="showDeleteConfirmation = false" class="cancel-button">
              Cancel
            </button>
            <button @click="confirmDelete" class="confirm-delete-button">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAgent } from '../../application/composables/useAgent';
import { createRepositories } from '../../infrastructure/factory';

export default {
  name: 'AgentView',
  setup() {
    const router = useRouter();
    
    // Get repositories from factory
    const { agentRepository, getUserId } = createRepositories();
    
    // Initialize agent composable with real repository
    const { 
      agents, 
      loading, 
      error, 
      loadAgents, 
      createAgent, 
      updateAgent,
      deleteAgent,
      hasAgents
    } = useAgent(agentRepository, getUserId);
    
    // Local state
    const selectedAgent = ref(null);
    const showCreateAgentModal = ref(false);
    const agentToEdit = ref(null);
    const showDeleteConfirmation = ref(false);
    const agentToDeleteId = ref(null);
    
    // Default form structure for creating/editing agents
    const defaultAgentForm = {
      name: '',
      type: 'conversational',
      description: '',
      permissions: {
        canSendEmail: false,
        canExecuteCommands: false,
        canAccessFiles: false,
        canCallApi: false,
        canAccessDatabase: false
      }
    };
    
    // Form for creating/editing agents
    const agentForm = reactive({ ...defaultAgentForm });
    
    // Load agents on component mount
    onMounted(() => {
      console.log('AgentView mounted, loading agents...');
      loadAgents();
    });
    
    // Format date for display
    const formatDate = (date) => {
      if (!date) return 'Unknown';
      
      const dateObj = date instanceof Date ? date : new Date(date);
      return dateObj.toLocaleString();
    };
    
    // Format permission name for display
    const formatPermissionName = (key) => {
      return key
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, (str) => str.toUpperCase())
        .replace(/can/i, '');
    };
    
    // Select an agent to view details
    const selectAgent = (agentId) => {
      const agent = agents.value.find(a => a.id === agentId);
      if (agent) {
        selectedAgent.value = agent;
      }
    };
    
    // Prepare to edit an agent
    const editAgent = (agent) => {
      // Close other modals
      selectedAgent.value = null;
      
      // Set up edit form
      agentToEdit.value = agent;
      
      // Copy agent data to form
      Object.assign(agentForm, {
        name: agent.name,
        type: agent.type,
        description: agent.description,
        permissions: { ...defaultAgentForm.permissions, ...(agent.permissions || {}) }
      });
    };
    
    // Cancel agent form
    const cancelAgentForm = () => {
      // Reset form
      Object.assign(agentForm, defaultAgentForm);
      
      // Close modals
      showCreateAgentModal.value = false;
      agentToEdit.value = null;
    };
    
    // Submit agent form for creation or update
    const submitAgentForm = async () => {
      try {
        if (agentToEdit.value) {
          // Update existing agent
          await updateAgent(agentToEdit.value.id, {
            name: agentForm.name,
            type: agentForm.type,
            description: agentForm.description,
            permissions: agentForm.permissions
          });
        } else {
          // Create new agent
          await createAgent({
            name: agentForm.name,
            type: agentForm.type,
            description: agentForm.description,
            permissions: agentForm.permissions
          });
        }
        
        // Reset form and close modal
        cancelAgentForm();
      } catch (err) {
        console.error('Error submitting agent form:', err);
      }
    };
    
    // Prepare to delete an agent
    const deleteAgentWithConfirm = (agentId) => {
      agentToDeleteId.value = agentId;
      showDeleteConfirmation.value = true;
      
      // Close other modals
      selectedAgent.value = null;
      cancelAgentForm();
    };
    
    // Confirm agent deletion
    const confirmDelete = async () => {
      if (!agentToDeleteId.value) return;
      
      try {
        await deleteAgent(agentToDeleteId.value);
        
        // Close confirmation modal
        showDeleteConfirmation.value = false;
        agentToDeleteId.value = null;
      } catch (err) {
        console.error('Error deleting agent:', err);
      }
    };
    
    // Navigate to chat with the selected agent
    const prepareAgentForChat = (agent) => {
      router.push({
        name: 'chat',
        params: { agentId: agent.id }
      });
    };
    
    return {
      // State
      agents,
      loading,
      error,
      hasAgents,
      selectedAgent,
      showCreateAgentModal,
      agentToEdit,
      agentForm,
      showDeleteConfirmation,
      
      // Methods
      loadAgents,
      formatDate,
      formatPermissionName,
      selectAgent,
      editAgent,
      cancelAgentForm,
      submitAgentForm,
      deleteAgentWithConfirm,
      confirmDelete,
      prepareAgentForChat
    };
  }
}
</script>

<style scoped>
.agent-view {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.agent-view h1 {
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

.loading-state, .error-state, .no-agents {
  text-align: center;
  padding: 2rem;
  background: #f9f9f9;
  border-radius: 8px;
  margin: 1rem 0;
}

.error-state {
  background: #fff5f5;
  color: #e53e3e;
}

.retry-button, .create-agent-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #3182ce;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.retry-button:hover, .create-agent-button:hover {
  background: #2b6cb0;
}

.agent-controls {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.agents-grid {
  display: flex;
  flex-direction: column;
}

.agent-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.agent-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.agent-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.agent-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.agent-card-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.agent-type {
  background: #ebf8ff;
  color: #3182ce;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.agent-description {
  color: #4a5568;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  line-height: 1.5;
}

.agent-card-footer {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.agent-updated {
  font-size: 0.8rem;
  color: #718096;
}

.agent-actions {
  display: flex;
  gap: 0.5rem;
}

.chat-button, .edit-button, .delete-button {
  padding: 0.4rem 0.75rem;
  font-size: 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.chat-button {
  background: #38a169;
  color: white;
}

.chat-button:hover {
  background: #2f855a;
}

.edit-button {
  background: #3182ce;
  color: white;
}

.edit-button:hover {
  background: #2b6cb0;
}

.delete-button {
  background: #e53e3e;
  color: white;
}

.delete-button:hover {
  background: #c53030;
}

/* Modal styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #718096;
}

.modal-body {
  padding: 1.5rem;
}

/* Agent detail styles */
.agent-detail-section {
  margin-bottom: 1.5rem;
}

.agent-detail-section h3 {
  margin-top: 0;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
  color: #4a5568;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.agent-detail-item {
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.permissions-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

.permission-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0.75rem;
  background: #f7fafc;
  border-radius: 4px;
}

.permission-name {
  font-weight: 500;
}

.permission-value {
  font-size: 0.8rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.permission-value.enabled {
  background: #c6f6d5;
  color: #22543d;
}

.permission-value.disabled {
  background: #fed7d7;
  color: #822727;
}

.agent-actions-footer {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

/* Form styles */
.agent-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #4a5568;
}

.form-group input[type="text"],
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.permissions-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

.permission-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
}

.cancel-button, .submit-button, .confirm-delete-button {
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.cancel-button {
  background: #e2e8f0;
  color: #4a5568;
}

.cancel-button:hover {
  background: #cbd5e0;
}

.submit-button {
  background: #3182ce;
  color: white;
}

.submit-button:hover {
  background: #2b6cb0;
}

.confirm-delete-button {
  background: #e53e3e;
  color: white;
}

.confirm-delete-button:hover {
  background: #c53030;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .agent-cards {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    max-height: 80vh;
  }
  
  .permissions-list, .permissions-checkboxes {
    grid-template-columns: 1fr;
  }
}
</style> 