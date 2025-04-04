import { ref, computed } from 'vue';

/**
 * User authentication composable
 * 
 * @returns {Object} User authentication state and methods
 */
export function useUser() {
  // State for user authentication
  const user = ref(null);
  const token = ref(localStorage.getItem('auth_token') || null);
  const loading = ref(false);
  const error = ref(null);
  
  // Computed properties
  const isAuthenticated = computed(() => !!token.value);
  const userId = computed(() => user.value?.id || localStorage.getItem('user_id') || null);
  
  /**
   * Initialize user data from localStorage if available
   */
  const initUser = () => {
    const userJson = localStorage.getItem('user_data');
    if (userJson) {
      try {
        user.value = JSON.parse(userJson);
        console.log('User data loaded from localStorage:', user.value);
      } catch (err) {
        console.error('Error parsing user data from localStorage:', err);
        localStorage.removeItem('user_data');
      }
    }
  };
  
  /**
   * Get the current user ID
   * @returns {string|null} User ID if available, null otherwise
   */
  const getUserId = () => {
    return userId.value;
  };
  
  /**
   * Login a user with credentials
   * 
   * @param {Object} credentials - User credentials
   * @param {string} credentials.email - User email or username
   * @param {string} credentials.password - User password
   * @returns {Promise<Object>} Logged in user data
   */
  const login = async (credentials) => {
    loading.value = true;
    error.value = null;
    
    try {
      console.log('Attempting login with credentials:', credentials.email);
      
      // Create a proper payload based on whether we have an email or username
      const payload = {
        password: credentials.password
      };
      
      // Check if the provided identifier includes @ to determine if it's an email
      if (credentials.email.includes('@')) {
        payload.email = credentials.email;
      } else {
        payload.username = credentials.email;
      }
      
      // Connect to the auth service through API gateway
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(payload),
        credentials: 'include'
      });
      
      // Check for HTTP errors
      if (!response.ok) {
        let errorMessage = 'Authentication failed';
        
        try {
          // Try to get error details from response
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorMessage;
        } catch (parseError) {
          console.error('Error parsing error response:', parseError);
        }
        
        throw new Error(errorMessage);
      }
      
      // Parse the successful response
      const data = await response.json();
      console.log('Auth response:', data);
      
      // Get the token from the response
      const authToken = data.token || data.access_token;
      
      if (!authToken) {
        throw new Error('No authentication token received');
      }
      
      // Get user data from response
      const userData = data.user || {
        id: data.user_id || '123',
        name: data.name || credentials.email,
        email: credentials.email
      };
      
      // Update state
      user.value = userData;
      token.value = authToken;
      
      // Store in localStorage
      localStorage.setItem('auth_token', authToken);
      localStorage.setItem('user_id', userData.id);
      localStorage.setItem('user_data', JSON.stringify(userData));
      
      return userData;
    } catch (err) {
      console.error('Login error:', err);
      error.value = err.message || 'Failed to login';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  /**
   * Log out the current user
   */
  const logout = async () => {
    // If we have a token, try to logout from the server
    if (token.value) {
      try {
        await fetch('/api/logout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${token.value}`
          },
          credentials: 'include'
        });
      } catch (err) {
        console.error('Logout error:', err);
        // Continue with local logout even if server logout fails
      }
    }
    
    // Clear state
    user.value = null;
    token.value = null;
    
    // Clear localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_data');
  };
  
  /**
   * Check and refresh authentication state
   */
  const checkAuthState = async () => {
    const storedToken = localStorage.getItem('auth_token');
    
    if (storedToken) {
      token.value = storedToken;
      initUser();
      
      // Optionally verify token with the server
      try {
        const response = await fetch('/api/verify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${storedToken}`
          },
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error('Token invalid');
        }
        
        // Token is valid, update user data if needed
        const data = await response.json();
        if (data.user) {
          user.value = data.user;
          localStorage.setItem('user_data', JSON.stringify(data.user));
        }
      } catch (err) {
        console.error('Token verification failed:', err);
        // Token is invalid, logout
        logout();
      }
    } else {
      user.value = null;
      token.value = null;
    }
  };
  
  // Initialize on composable creation
  checkAuthState();
  
  return {
    // State
    user,
    token,
    loading,
    error,
    isAuthenticated,
    userId,
    
    // Methods
    login,
    logout,
    getUserId,
    checkAuthState
  };
} 