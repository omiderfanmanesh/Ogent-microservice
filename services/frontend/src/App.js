import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Context Providers
import { AuthProvider } from './contexts/AuthContext';

// Layout
import MainLayout from './components/layout/MainLayout';

// Auth Components
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Unauthorized from './pages/Unauthorized';

// Main Pages
import Dashboard from './pages/Dashboard';
import AgentList from './pages/agents/AgentList';
import AgentDetail from './pages/agents/AgentDetail';
import CreateEditAgent from './pages/agents/CreateEditAgent';

// Execution pages
import ExecutionList from './pages/executions/ExecutionList';
import ExecutionDetail from './pages/executions/ExecutionDetail';
import CommandExecutionPage from './pages/executions/CommandExecutionPage';

// Admin Pages (if needed)
import UserList from './pages/admin/UserList';
import RoleList from './pages/admin/RoleList';

// Create a theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/unauthorized" element={<Unauthorized />} />
            
            {/* Protected Routes wrapped in MainLayout */}
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <Dashboard />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <Dashboard />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />
            
            {/* Agent Routes */}
            <Route 
              path="/agents" 
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <AgentList />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/agents/new" 
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <CreateEditAgent />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/agents/:id" 
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <AgentDetail />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/agents/:id/edit" 
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <CreateEditAgent />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />

            {/* Execution Routes */}
            <Route 
              path="/executions" 
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <ExecutionList />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/executions/:id" 
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <ExecutionDetail />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/executions/command" 
              element={
                <ProtectedRoute requiredPermission="run agents">
                  <MainLayout>
                    <CommandExecutionPage />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />
            
            {/* Admin Routes */}
            <Route 
              path="/admin/users" 
              element={
                <ProtectedRoute requiredRole="admin">
                  <MainLayout>
                    <UserList />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/admin/roles" 
              element={
                <ProtectedRoute requiredRole="admin">
                  <MainLayout>
                    <RoleList />
                  </MainLayout>
                </ProtectedRoute>
              } 
            />
            
            {/* Not found - redirect to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App; 