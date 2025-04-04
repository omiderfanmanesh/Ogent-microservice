<template>
  <div class="chat-view">
    <div class="chat-header">
      <h1 v-if="currentAgent">Chat with {{ currentAgent.name }}</h1>
      <h1 v-else>Select an Agent to Chat With</h1>
      
      <div v-if="currentAgent" class="agent-info">
        <span class="agent-type">{{ currentAgent.type }}</span>
        <button @click="backToAgents" class="back-button">
          Back to Agents
        </button>
      </div>
    </div>
    
    <div v-if="!currentAgent && !loading" class="select-agent-container">
      <p>Please select an agent to start chatting</p>
      <div class="agent-list">
        <div 
          v-for="agent in agents" 
          :key="agent.id" 
          class="agent-card"
          @click="selectAgent(agent.id)"
        >
          <h3>{{ agent.name }}</h3>
          <p>{{ agent.description }}</p>
          <span class="agent-type">{{ agent.type }}</span>
        </div>
      </div>
    </div>
    
    <div v-else-if="loading" class="loading-container">
      <p>Loading...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <p>Error: {{ error }}</p>
      <button @click="loadAgents" class="retry-button">Retry</button>
    </div>
    
    <div v-else-if="currentAgent" class="chat-container">
      <div class="messages-container" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-chat">
          <p>No messages yet. Start a conversation with {{ currentAgent.name }}!</p>
        </div>
        
        <div v-else class="messages">
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            :class="['message', message.role === 'user' ? 'user-message' : 'agent-message']"
          >
            <div class="message-content">
              <p>{{ message.content }}</p>
            </div>
            <div class="message-time">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="isExecuting" class="executing-indicator">
        <p>{{ currentAgent.name }} is thinking...</p>
      </div>
      
      <div class="input-container">
        <textarea 
          v-model="userInput" 
          placeholder="Type your message here..."
          @keydown.enter.prevent="sendMessage"
          :disabled="isExecuting"
          ref="userInputField"
          rows="3"
        ></textarea>
        <button 
          @click="sendMessage" 
          :disabled="!userInput.trim() || isExecuting"
          class="send-button"
        >
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAgent } from '../../application/composables/useAgent';
import { createRepositories } from '../../infrastructure/factory';

export default {
  name: 'ChatView',
  setup() {
    const route = useRoute();
    const router = useRouter();
    
    // Get repositories from factory
    const { agentRepository, getUserId } = createRepositories();
    
    // Initialize agent composable with real repository
    const { 
      agents, 
      currentAgent,
      loading, 
      error, 
      loadAgents,
      getAgent,
      executeAgent,
    } = useAgent(agentRepository, getUserId);
    
    // Local state
    const userInput = ref('');
    const messages = ref([]);
    const isExecuting = ref(false);
    const messagesContainer = ref(null);
    const userInputField = ref(null);
    
    // Check for agentId in the route params
    onMounted(async () => {
      console.log('ChatView mounted');
      await loadAgents();
      
      const agentId = route.params.agentId;
      console.log('Route agent ID:', agentId);
      
      if (agentId) {
        await selectAgent(agentId);
      }
      
      // Focus the input field if an agent is selected
      if (currentAgent.value) {
        focusInputField();
      }
    });
    
    // Watch for changes in currentAgent
    watch(currentAgent, () => {
      if (currentAgent.value) {
        messages.value = [];
        
        // Add a welcome message
        messages.value.push({
          role: 'assistant',
          content: `Hello! I'm ${currentAgent.value.name}. How can I assist you today?`,
          timestamp: new Date()
        });
        
        focusInputField();
      }
    });
    
    // Format timestamp
    const formatTime = (timestamp) => {
      if (!timestamp) return '';
      
      const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };
    
    // Select an agent to chat with
    const selectAgent = async (agentId) => {
      console.log('Selecting agent with ID:', agentId);
      try {
        await getAgent(agentId);
        
        // Update the URL without reloading the page
        if (route.params.agentId !== agentId) {
          router.replace({
            name: 'chat',
            params: { agentId }
          });
        }
      } catch (err) {
        console.error('Error selecting agent:', err);
      }
    };
    
    // Navigate back to agents view
    const backToAgents = () => {
      router.push({ name: 'agents' });
    };
    
    // Send a message to the current agent
    const sendMessage = async () => {
      if (!userInput.value.trim() || !currentAgent.value || isExecuting.value) return;
      
      // Add user message to chat
      const userMessage = {
        role: 'user',
        content: userInput.value.trim(),
        timestamp: new Date()
      };
      messages.value.push(userMessage);
      
      // Clear input
      const sentMessage = userInput.value;
      userInput.value = '';
      
      // Scroll to bottom
      await scrollToBottom();
      
      // Execute agent
      isExecuting.value = true;
      
      try {
        console.log('Executing agent:', currentAgent.value.id);
        const result = await executeAgent(currentAgent.value.id, {
          input: sentMessage
        });
        
        console.log('Agent execution result:', result);
        
        // Add agent response to chat
        messages.value.push({
          role: 'assistant',
          content: result.output,
          timestamp: new Date()
        });
      } catch (err) {
        console.error('Error executing agent:', err);
        
        // Add error message to chat
        messages.value.push({
          role: 'assistant',
          content: `Sorry, I encountered an error: ${err.message}`,
          timestamp: new Date()
        });
      } finally {
        isExecuting.value = false;
        
        // Scroll to bottom and focus input field
        await scrollToBottom();
        focusInputField();
      }
    };
    
    // Scroll chat to bottom
    const scrollToBottom = async () => {
      await nextTick();
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    };
    
    // Focus the input field
    const focusInputField = () => {
      nextTick(() => {
        if (userInputField.value) {
          userInputField.value.focus();
        }
      });
    };
    
    return {
      // State
      agents,
      currentAgent,
      loading,
      error,
      userInput,
      messages,
      isExecuting,
      messagesContainer,
      userInputField,
      
      // Methods
      loadAgents,
      formatTime,
      selectAgent,
      backToAgents,
      sendMessage
    };
  }
}
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: calc(100vh - 60px);
  padding: 1rem;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1rem;
}

.chat-header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.agent-type {
  background: #ebf8ff;
  color: #3182ce;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.back-button {
  padding: 0.5rem 1rem;
  background: #4a5568;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.back-button:hover {
  background: #2d3748;
}

.select-agent-container, .loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
  text-align: center;
  padding: 2rem;
}

.agent-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  width: 100%;
  max-width: 900px;
  margin-top: 1.5rem;
}

.agent-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: left;
}

.agent-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.agent-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.agent-card p {
  color: #4a5568;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.chat-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  height: 100%;
}

.messages-container {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
  margin-bottom: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.empty-chat {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #a0aec0;
  font-style: italic;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  max-width: 80%;
  padding: 1rem;
  border-radius: 8px;
}

.user-message {
  align-self: flex-end;
  background-color: #4299e1;
  color: white;
}

.agent-message {
  align-self: flex-start;
  background-color: white;
  color: #2d3748;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-content p {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-time {
  margin-top: 0.5rem;
  font-size: 0.7rem;
  opacity: 0.7;
  text-align: right;
}

.executing-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.5rem;
  color: #4a5568;
  font-style: italic;
}

.input-container {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.05);
}

.input-container textarea {
  flex-grow: 1;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
}

.input-container textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.2);
}

.send-button {
  align-self: flex-end;
  padding: 0.75rem 1.5rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.send-button:hover:not(:disabled) {
  background: #3182ce;
}

.send-button:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.retry-button {
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

.retry-button:hover {
  background: #2b6cb0;
}

/* Responsive styling */
@media (max-width: 768px) {
  .chat-view {
    padding: 0.5rem;
    max-height: calc(100vh - 50px);
  }
  
  .message {
    max-width: 90%;
  }
  
  .agent-list {
    grid-template-columns: 1fr;
  }
}
</style> 