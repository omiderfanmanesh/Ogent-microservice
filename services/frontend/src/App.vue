<template>
  <div class="app">
    <header class="app-header">
      <h1 class="app-title">Ogent AI</h1>
      <nav class="app-nav">
        <router-link to="/agents" class="nav-link">Agents</router-link>
        <router-link to="/chat" class="nav-link">Chat</router-link>
      </nav>
      <div class="user-actions">
        <button v-if="isAuthenticated" @click="logout" class="logout-button">
          Logout
        </button>
        <router-link v-else to="/login" class="login-link">
          Login
        </router-link>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <footer class="app-footer">
      <p>&copy; 2023 Ogent AI - Domain-Driven Design Microservice Application</p>
    </footer>
  </div>
</template>

<script>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUser } from './application/composables/useUser';

export default {
  name: 'App',
  setup() {
    const router = useRouter();
    const { isAuthenticated, logout, checkAuthState } = useUser();

    onMounted(() => {
      console.log('App mounted, checking auth state');
      checkAuthState();
    });

    // Logout function
    const handleLogout = () => {
      console.log('Logging out');
      logout();
      router.push('/login');
    };

    return {
      isAuthenticated,
      logout: handleLogout
    };
  }
}
</script>

<style>
/* Base styles */
:root {
  --color-primary: #3182ce;
  --color-primary-dark: #2b6cb0;
  --color-secondary: #4a5568;
  --color-secondary-dark: #2d3748;
  --color-accent: #38a169;
  --color-accent-dark: #2f855a;
  --color-danger: #e53e3e;
  --color-danger-dark: #c53030;
  --color-gray-100: #f7fafc;
  --color-gray-200: #edf2f7;
  --color-gray-300: #e2e8f0;
  --color-gray-400: #cbd5e0;
  --color-gray-500: #a0aec0;
  --color-gray-600: #718096;
  --color-gray-700: #4a5568;
  --color-gray-800: #2d3748;
  --color-gray-900: #1a202c;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  color: var(--color-gray-900);
  background-color: var(--color-gray-100);
  line-height: 1.5;
  font-size: 16px;
}

/* Layout */
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-title {
  color: var(--color-primary);
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.app-nav {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  color: var(--color-gray-700);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
  transition: color 0.2s, border-color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.user-actions {
  display: flex;
  align-items: center;
}

.logout-button {
  background-color: var(--color-gray-200);
  color: var(--color-gray-700);
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-button:hover {
  background-color: var(--color-gray-300);
}

.login-link {
  background-color: var(--color-primary);
  color: white;
  text-decoration: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.login-link:hover {
  background-color: var(--color-primary-dark);
}

.app-main {
  flex: 1;
  padding: 0;
  max-width: 100%;
}

.app-footer {
  background-color: var(--color-gray-800);
  color: var(--color-gray-300);
  text-align: center;
  padding: 1rem;
  font-size: 0.875rem;
}

/* Responsive styles */
@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    padding: 1rem;
    gap: 0.75rem;
  }
  
  .app-nav {
    width: 100%;
    justify-content: center;
  }
  
  .user-actions {
    width: 100%;
    justify-content: center;
  }
}
</style> 