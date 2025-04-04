<template>
  <div class="agent-card" :class="{ 'agent-card--active': isActive }">
    <div class="agent-card__header">
      <h3 class="agent-card__title">{{ agent.name }}</h3>
      <span class="agent-card__type">{{ formatAgentType(agent.type) }}</span>
    </div>
    
    <div class="agent-card__body">
      <div class="agent-card__info">
        <div class="agent-card__info-item">
          <span class="agent-card__info-label">Created</span>
          <span class="agent-card__info-value">{{ formatDate(agent.createdAt) }}</span>
        </div>
        <div class="agent-card__info-item">
          <span class="agent-card__info-label">Last Updated</span>
          <span class="agent-card__info-value">{{ formatDate(agent.updatedAt) }}</span>
        </div>
      </div>
      
      <div class="agent-card__permissions">
        <div
          v-for="(value, key) in agent.permissions"
          :key="key"
          class="agent-card__permission"
          :class="{ 'agent-card__permission--enabled': value }"
        >
          {{ formatPermissionName(key) }}
        </div>
      </div>
    </div>
    
    <div class="agent-card__actions">
      <button
        class="agent-card__action-btn agent-card__action-btn--execute"
        @click="$emit('execute', agent.id)"
      >
        Execute
      </button>
      <button
        class="agent-card__action-btn agent-card__action-btn--edit"
        @click="$emit('edit', agent.id)"
      >
        Edit
      </button>
      <button
        class="agent-card__action-btn agent-card__action-btn--delete"
        @click="confirmDelete"
      >
        Delete
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AgentCard',
  
  props: {
    /**
     * Agent entity to display
     */
    agent: {
      type: Object,
      required: true
    },
    
    /**
     * Whether this agent is active/selected
     */
    isActive: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['execute', 'edit', 'delete'],
  
  methods: {
    /**
     * Format agent type for display
     * @param {string} type - Agent type
     * @returns {string} Formatted type
     */
    formatAgentType(type) {
      const types = {
        'conversational': 'Conversational',
        'command': 'Command Executor',
        'function': 'Function Caller'
      };
      
      return types[type] || type;
    },
    
    /**
     * Format date for display
     * @param {Date|string} date - Date to format
     * @returns {string} Formatted date
     */
    formatDate(date) {
      if (!date) return 'N/A';
      
      const dateObj = date instanceof Date ? date : new Date(date);
      return dateObj.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },
    
    /**
     * Format permission name for display
     * @param {string} permission - Permission key
     * @returns {string} Formatted permission name
     */
    formatPermissionName(permission) {
      return permission
        .replace(/([A-Z])/g, ' $1')
        .replace(/_/g, ' ')
        .replace(/^./, str => str.toUpperCase());
    },
    
    /**
     * Confirm deletion before emitting event
     */
    confirmDelete() {
      if (confirm(`Are you sure you want to delete the agent "${this.agent.name}"?`)) {
        this.$emit('delete', this.agent.id);
      }
    }
  }
};
</script>

<style scoped>
.agent-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin-bottom: 16px;
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.agent-card--active {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
  border-left: 4px solid #4c6ef5;
}

.agent-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.agent-card__title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.agent-card__type {
  font-size: 14px;
  font-weight: 500;
  color: #6c757d;
  background-color: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.agent-card__body {
  margin-bottom: 16px;
}

.agent-card__info {
  display: flex;
  margin-bottom: 12px;
}

.agent-card__info-item {
  margin-right: 16px;
}

.agent-card__info-label {
  font-size: 12px;
  color: #6c757d;
  display: block;
}

.agent-card__info-value {
  font-size: 14px;
}

.agent-card__permissions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.agent-card__permission {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  background-color: #e9ecef;
  color: #495057;
}

.agent-card__permission--enabled {
  background-color: #d8f3dc;
  color: #2d6a4f;
}

.agent-card__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.agent-card__action-btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.agent-card__action-btn--execute {
  background-color: #4c6ef5;
  color: white;
}

.agent-card__action-btn--execute:hover {
  background-color: #3b5bdb;
}

.agent-card__action-btn--edit {
  background-color: #f8f9fa;
  color: #212529;
}

.agent-card__action-btn--edit:hover {
  background-color: #e9ecef;
}

.agent-card__action-btn--delete {
  background-color: #fff0f3;
  color: #e03131;
}

.agent-card__action-btn--delete:hover {
  background-color: #ffe3e3;
}
</style> 