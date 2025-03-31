import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Divider,
  Tab,
  Tabs,
  Snackbar
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import apiService from '../../services/api';

// JSON Editor component
const JsonEditor = ({ value, onChange, error }) => {
  const [localValue, setLocalValue] = useState('');
  const [localError, setLocalError] = useState('');

  useEffect(() => {
    try {
      setLocalValue(JSON.stringify(value || {}, null, 2));
      setLocalError('');
    } catch (err) {
      setLocalError('Invalid JSON structure');
    }
  }, [value]);

  const handleChange = (e) => {
    const newValue = e.target.value;
    setLocalValue(newValue);
    
    try {
      const parsedJson = JSON.parse(newValue);
      onChange(parsedJson);
      setLocalError('');
    } catch (err) {
      setLocalError('Invalid JSON: ' + err.message);
    }
  };

  return (
    <TextField
      fullWidth
      multiline
      rows={12}
      variant="outlined"
      value={localValue}
      onChange={handleChange}
      error={!!localError || !!error}
      helperText={localError || error}
      sx={{
        fontFamily: 'monospace',
        '& .MuiInputBase-input': {
          fontFamily: 'monospace',
        }
      }}
    />
  );
};

const CreateEditAgent = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = !!id;
  
  // Form state
  const [agent, setAgent] = useState({
    name: '',
    description: '',
    agent_type: 'command',
    configuration: {}
  });
  
  // UI state
  const [loading, setLoading] = useState(isEditMode);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [formErrors, setFormErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');

  // Load agent data if in edit mode
  useEffect(() => {
    if (isEditMode) {
      fetchAgentData();
    }
  }, [id]);

  const fetchAgentData = async () => {
    try {
      setLoading(true);
      const agentData = await apiService.agents.getById(id);
      setAgent(agentData);
      setError(null);
    } catch (err) {
      console.error('Error fetching agent:', err);
      setError('Failed to load agent data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setAgent((prev) => ({
      ...prev,
      [name]: value
    }));
    
    // Clear field-specific error when user edits the field
    if (formErrors[name]) {
      setFormErrors((prev) => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const handleConfigChange = (newConfig) => {
    setAgent((prev) => ({
      ...prev,
      configuration: newConfig
    }));
    
    // Clear configuration error
    if (formErrors.configuration) {
      setFormErrors((prev) => ({
        ...prev,
        configuration: undefined
      }));
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const validateForm = () => {
    const errors = {};
    
    if (!agent.name.trim()) {
      errors.name = 'Name is required';
    }
    
    if (!agent.agent_type) {
      errors.agent_type = 'Agent type is required';
    }
    
    try {
      // Make sure configuration is valid for the selected agent type
      const config = agent.configuration;
      
      if (agent.agent_type === 'command') {
        if (!config.command) {
          errors.configuration = 'Command is required for Command agent';
        }
      } else if (agent.agent_type === 'sql') {
        if (!config.query) {
          errors.configuration = 'Query is required for SQL agent';
        }
      } else if (agent.agent_type === 'custom') {
        if (!config.prompt) {
          errors.configuration = 'Prompt is required for Custom agent';
        }
      }
    } catch (err) {
      errors.configuration = 'Invalid configuration format';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      // Show errors and focus on Basic Info tab if there are errors there
      if (formErrors.name || formErrors.agent_type || formErrors.description) {
        setActiveTab(0);
      }
      return;
    }
    
    try {
      setSaving(true);
      
      if (isEditMode) {
        await apiService.agents.update(id, agent);
        setSuccessMessage('Agent updated successfully');
      } else {
        const result = await apiService.agents.create(agent);
        setSuccessMessage('Agent created successfully');
        // Navigate to the new agent after a short delay
        setTimeout(() => {
          navigate(`/agents/${result.id}`);
        }, 1500);
      }
    } catch (err) {
      console.error('Error saving agent:', err);
      setError('Failed to save agent: ' + (err.message || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  // Get default configuration template based on agent type
  const getDefaultConfig = (type) => {
    switch (type) {
      case 'command':
        return { command: '', arguments: [], env: {} };
      case 'sql':
        return { query: '', parameters: {} };
      case 'custom':
        return { prompt: '', model: 'gpt-4', temperature: 0.7 };
      default:
        return {};
    }
  };

  // When agent type changes, provide a default configuration template
  const handleAgentTypeChange = (e) => {
    const newType = e.target.value;
    setAgent((prev) => ({
      ...prev,
      agent_type: newType,
      configuration: getDefaultConfig(newType)
    }));
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Button 
          variant="outlined" 
          startIcon={<BackIcon />}
          onClick={() => navigate('/agents')}
          sx={{ mb: 2 }}
        >
          Back to Agents
        </Button>
        
        <Typography variant="h4" component="h1">
          {isEditMode ? 'Edit Agent' : 'Create New Agent'}
        </Typography>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={() => setSuccessMessage('')}
        message={successMessage}
      />
      
      <Paper sx={{ p: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            aria-label="agent configuration tabs"
          >
            <Tab label="Basic Info" />
            <Tab label="Configuration" />
          </Tabs>
        </Box>
        
        <Box component="form" onSubmit={handleSubmit}>
          {/* Basic Info Tab */}
          <Box sx={{ p: 2, display: activeTab === 0 ? 'block' : 'none' }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  label="Agent Name"
                  name="name"
                  value={agent.name}
                  onChange={handleChange}
                  error={!!formErrors.name}
                  helperText={formErrors.name}
                />
              </Grid>
              
              <Grid item xs={12}>
                <FormControl fullWidth error={!!formErrors.agent_type}>
                  <InputLabel id="agent-type-label">Agent Type</InputLabel>
                  <Select
                    labelId="agent-type-label"
                    value={agent.agent_type}
                    label="Agent Type"
                    name="agent_type"
                    onChange={handleAgentTypeChange}
                  >
                    <MenuItem value="command">Command</MenuItem>
                    <MenuItem value="sql">SQL</MenuItem>
                    <MenuItem value="custom">Custom</MenuItem>
                  </Select>
                  {formErrors.agent_type && (
                    <Typography color="error" variant="caption">
                      {formErrors.agent_type}
                    </Typography>
                  )}
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  name="description"
                  multiline
                  rows={3}
                  value={agent.description || ''}
                  onChange={handleChange}
                />
              </Grid>
            </Grid>
          </Box>
          
          {/* Configuration Tab */}
          <Box sx={{ p: 2, display: activeTab === 1 ? 'block' : 'none' }}>
            <Typography variant="h6" gutterBottom>
              {agent.agent_type.charAt(0).toUpperCase() + agent.agent_type.slice(1)} Agent Configuration
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ mb: 2 }}>
              {agent.agent_type === 'command' && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Configure the command to execute, arguments, and environment variables.
                </Typography>
              )}
              
              {agent.agent_type === 'sql' && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Configure the SQL query to execute and any parameters.
                </Typography>
              )}
              
              {agent.agent_type === 'custom' && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Configure the prompt, model, and other parameters for a custom AI agent.
                </Typography>
              )}
            </Box>
            
            <JsonEditor
              value={agent.configuration}
              onChange={handleConfigChange}
              error={formErrors.configuration}
            />
          </Box>
          
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              startIcon={saving ? <CircularProgress size={24} /> : <SaveIcon />}
              type="submit"
              disabled={saving}
            >
              {saving ? 'Saving...' : (isEditMode ? 'Update Agent' : 'Create Agent')}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default CreateEditAgent; 