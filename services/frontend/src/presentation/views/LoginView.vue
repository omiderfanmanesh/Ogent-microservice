<template>
  <div class="login-view">
    <div class="login-view__container">
      <div class="login-view__header">
        <h1 class="login-view__title">Ogent</h1>
        <p class="login-view__subtitle">AI Agent Platform</p>
      </div>
      
      <div class="login-view__card">
        <h2 class="login-view__card-title">Sign In</h2>
        
        <form class="login-view__form" @submit.prevent="login">
          <div class="login-view__form-group">
            <label class="login-view__form-label">Username or Email</label>
            <input 
              v-model="credentials.username" 
              class="login-view__form-input" 
              type="text" 
              placeholder="Enter your username or email"
              :disabled="loading"
              required
            />
          </div>
          
          <div class="login-view__form-group">
            <label class="login-view__form-label">Password</label>
            <input 
              v-model="credentials.password" 
              class="login-view__form-input" 
              type="password" 
              placeholder="Enter your password"
              :disabled="loading"
              required
            />
          </div>
          
          <div v-if="error" class="login-view__error">
            {{ error }}
          </div>
          
          <button 
            type="submit" 
            class="login-view__submit-btn"
            :disabled="loading || !isFormValid"
          >
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUser } from '../../application/composables/useUser';

export default {
  name: 'LoginView',
  
  setup() {
    const router = useRouter();
    const { login: authLogin, loading, error } = useUser();
    
    const credentials = ref({
      username: '',
      password: ''
    });
    
    const isFormValid = computed(() => {
      return credentials.value.username.trim() !== '' && 
             credentials.value.password.trim() !== '';
    });
    
    const login = async () => {
      if (!isFormValid.value) return;
      
      try {
        console.log('Login attempt with:', credentials.value.username);
        
        // Try authenticating with real backend
        await authLogin({
          email: credentials.value.username,
          password: credentials.value.password
        });
        
        console.log('Authentication successful');
        
        // Check if there's a redirect URL stored
        const redirectPath = localStorage.getItem('login_redirect');
        
        if (redirectPath) {
          // Clear the stored redirect path
          localStorage.removeItem('login_redirect');
          router.push(redirectPath);
        } else {
          // Default redirect to agents page
          router.push('/agents');
        }
      } catch (err) {
        console.error('Login error:', err);
        // Error is already handled by the useUser composable
      }
    };
    
    return {
      credentials,
      loading,
      error,
      isFormValid,
      login
    };
  }
};
</script>

<style scoped>
.login-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 24px;
}

.login-view__container {
  width: 100%;
  max-width: 400px;
}

.login-view__header {
  text-align: center;
  margin-bottom: 24px;
}

.login-view__title {
  font-size: 32px;
  font-weight: 700;
  color: #4c6ef5;
  margin: 0;
}

.login-view__subtitle {
  color: #6c757d;
  margin: 8px 0 0;
}

.login-view__card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.login-view__card-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 24px;
  text-align: center;
}

.login-view__form-group {
  margin-bottom: 16px;
}

.login-view__form-label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
}

.login-view__form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-family: inherit;
  font-size: 16px;
}

.login-view__form-input:focus {
  border-color: #4c6ef5;
  outline: none;
  box-shadow: 0 0 0 2px rgba(76, 110, 245, 0.25);
}

.login-view__error {
  color: #e03131;
  margin-bottom: 16px;
  font-size: 14px;
}

.login-view__submit-btn {
  width: 100%;
  background-color: #4c6ef5;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 12px 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.login-view__submit-btn:hover {
  background-color: #3b5bdb;
}

.login-view__submit-btn:disabled {
  background-color: #adb5bd;
  cursor: not-allowed;
}
</style> 