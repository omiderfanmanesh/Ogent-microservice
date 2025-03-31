import { io } from 'socket.io-client';

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.listeners = new Map();
    this.executionListeners = new Map();
    
    // Get the socket service URL from environment variables or use a default
    this.socketUrl = process.env.REACT_APP_SOCKET_SERVICE_URL || 'http://localhost:3002';
  }

  connect(token) {
    if (this.socket) {
      this.disconnect();
    }

    this.socket = io(this.socketUrl, {
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    this.setupListeners();
    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
      
      // Clear all execution listeners
      this.executionListeners.clear();
    }
  }

  setupListeners() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('Connected to socket server');
      this.isConnected = true;
      this.notifyListeners('connect');
    });

    this.socket.on('disconnect', (reason) => {
      console.log(`Disconnected from socket server: ${reason}`);
      this.isConnected = false;
      this.notifyListeners('disconnect', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error.message);
      this.notifyListeners('error', error.message);
    });

    this.socket.on('execution-started', (data) => {
      console.log('Execution started:', data);
      this.notifyListeners('execution-started', data);
    });

    this.socket.on('execution-status', (data) => {
      console.log('Execution status update:', data);
      this.notifyListeners('execution-status', data);
      
      // Notify specific execution listeners
      if (data.executionId) {
        const listeners = this.executionListeners.get(data.executionId) || [];
        listeners.forEach(callback => callback(data));
      }
    });
  }

  // Add a general event listener
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    
    this.listeners.get(event).push(callback);
    return () => this.off(event, callback);
  }

  // Remove a general event listener
  off(event, callback) {
    if (!this.listeners.has(event)) return;
    
    const listeners = this.listeners.get(event);
    const index = listeners.indexOf(callback);
    
    if (index !== -1) {
      listeners.splice(index, 1);
    }
  }

  // Notify all listeners for an event
  notifyListeners(event, ...args) {
    const listeners = this.listeners.get(event) || [];
    listeners.forEach(callback => callback(...args));
  }

  // Join an execution room to receive updates for a specific execution
  joinExecution(executionId, callback) {
    if (!this.socket || !this.isConnected) {
      console.error('Cannot join execution: Socket not connected');
      return null;
    }

    this.socket.emit('join-execution', executionId);
    
    // Add execution-specific listener
    if (callback) {
      if (!this.executionListeners.has(executionId)) {
        this.executionListeners.set(executionId, []);
      }
      
      this.executionListeners.get(executionId).push(callback);
      
      // Return a function to unsubscribe
      return () => {
        const listeners = this.executionListeners.get(executionId) || [];
        const index = listeners.indexOf(callback);
        
        if (index !== -1) {
          listeners.splice(index, 1);
        }
        
        // If no more listeners, leave the execution room
        if (listeners.length === 0) {
          this.leaveExecution(executionId);
        }
      };
    }
  }

  // Leave an execution room
  leaveExecution(executionId) {
    if (!this.socket || !this.isConnected) return;
    
    this.socket.emit('leave-execution', executionId);
    this.executionListeners.delete(executionId);
  }
}

// Create a singleton instance
const socketService = new SocketService();

export default socketService; 