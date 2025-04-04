import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'

// Import views
import AgentView from './presentation/views/AgentView.vue'
import LoginView from './presentation/views/LoginView.vue'
import ChatView from './presentation/views/ChatView.vue'

// For debugging
console.log('Initializing Vue app with version:', import.meta.env.MODE);

// Add global error handling
window.addEventListener('error', (event) => {
  console.error('Global error caught:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise Rejection:', event.reason);
});

try {
  // Create the router with base URL
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', redirect: '/agents' }, 
      { path: '/login', name: 'login', component: LoginView, meta: { requiresAuth: false } },
      { path: '/agents', name: 'agents', component: AgentView, meta: { requiresAuth: true } },
      { path: '/chat/:agentId?', name: 'chat', component: ChatView, meta: { requiresAuth: true } },
    ]
  });

  // Authentication guard
  router.beforeEach((to, from, next) => {
    console.log(`Router: Navigating from "${from.fullPath}" to "${to.fullPath}"`);
    
    // Check if the route requires authentication
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    
    // Get auth token from localStorage
    const hasToken = !!localStorage.getItem('auth_token');
    
    if (requiresAuth && !hasToken) {
      console.log('Authentication required, redirecting to login');
      // Store the intended destination to redirect after login
      localStorage.setItem('login_redirect', to.fullPath);
      next({ name: 'login' });
    } else {
      // Continue to the route
      next();
    }
  });

  // Create the Pinia store
  const pinia = createPinia();

  // Create and mount the app
  const app = createApp(App);

  app.use(pinia);
  app.use(router);

  // Mount with debugging
  console.log('Mounting app to #app element');
  app.mount('#app');
} catch (error) {
  console.error('Error initializing Vue app:', error);
} 