import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Button, 
  Grid, 
  TextField,
  Divider,
  Chip,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { 
  PlayArrow as RunIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
  ArrowBack as BackIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import apiService from '../../services/api';

const AgentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [agent, setAgent] = useState(null);
  const [recentExecutions, setRecentExecutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [runDialogOpen, setRunDialogOpen] = useState(false);
  const [input, setInput] = useState('');
  const [executing, setExecuting] = useState(false);

  const fetchAgentData = async () => {
    try {
      setLoading(true);
      
      // Fetch agent details
      const agentData = await apiService.agents.getById(id);
      setAgent(agentData);
      
      // Fetch recent executions for this agent
      const executionsData = await apiService.executions.list({ 
        agent_id: id,
        limit: 5,
        sort: 'created_at:desc'
      });
      setRecentExecutions(executionsData.items || []);
      
      setError(null);
    } catch (err) {
      console.error('Error fetching agent data:', err);
      setError('Failed to load agent data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgentData();
  }, [id]);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this agent?')) {
      try {
        await apiService.agents.delete(id);
        navigate('/agents');
      } catch (err) {
        console.error('Error deleting agent:', err);
        setError('Failed to delete agent. Please try again.');
      }
    }
  };

  const handleRunAgent = async () => {
    try {
      setExecuting(true);
      const result = await apiService.executions.create(id, { input });
      setRunDialogOpen(false);
      setInput('');
      
      // Navigate to execution detail
      navigate(`/executions/${result.id}`);
    } catch (err) {
      console.error('Error running agent:', err);
      setError('Failed to run agent. Please try again.');
    } finally {
      setExecuting(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getAgentTypeLabel = (type) => {
    let color = 'primary';
    
    switch (type) {
      case 'command':
        color = 'primary';
        break;
      case 'sql':
        color = 'success';
        break;
      case 'custom':
        color = 'warning';
        break;
      default:
        color = 'default';
    }
    
    return (
      <Chip
        label={type.toUpperCase()}
        color={color}
        size="small"
      />
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography color="error">{error}</Typography>
        <Button 
          variant="outlined" 
          startIcon={<BackIcon />}
          onClick={() => navigate('/agents')}
          sx={{ mt: 2 }}
        >
          Back to Agents
        </Button>
      </Container>
    );
  }

  if (!agent) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography>Agent not found</Typography>
        <Button 
          variant="outlined" 
          startIcon={<BackIcon />}
          onClick={() => navigate('/agents')}
          sx={{ mt: 2 }}
        >
          Back to Agents
        </Button>
      </Container>
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
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1">
            {agent.name}
          </Typography>
          
          <Box>
            <Button 
              variant="outlined" 
              startIcon={<HistoryIcon />}
              onClick={() => navigate(`/executions?agent_id=${id}`)}
              sx={{ mr: 1 }}
            >
              Execution History
            </Button>
            <Button 
              variant="outlined" 
              startIcon={<EditIcon />}
              onClick={() => navigate(`/agents/${id}/edit`)}
              sx={{ mr: 1 }}
            >
              Edit
            </Button>
            <Button 
              variant="outlined" 
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDelete}
              sx={{ mr: 1 }}
            >
              Delete
            </Button>
            <Button 
              variant="contained" 
              startIcon={<RunIcon />}
              onClick={() => setRunDialogOpen(true)}
            >
              Run Agent
            </Button>
          </Box>
        </Box>
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Agent Details
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Agent Type
                </Typography>
                <Box sx={{ mt: 1 }}>
                  {getAgentTypeLabel(agent.agent_type)}
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Created By
                </Typography>
                <Typography variant="body1">
                  {agent.user_id || 'N/A'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Created At
                </Typography>
                <Typography variant="body1">
                  {formatDate(agent.created_at)}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="text.secondary">
                  Last Updated
                </Typography>
                <Typography variant="body1">
                  {formatDate(agent.updated_at)}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">
                  Description
                </Typography>
                <Typography variant="body1">
                  {agent.description || 'No description provided'}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
          
          {agent.configuration && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Configuration
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Box component="pre" sx={{ 
                p: 2, 
                bgcolor: 'grey.100', 
                borderRadius: 1,
                maxHeight: 300,
                overflow: 'auto'
              }}>
                {JSON.stringify(agent.configuration, null, 2)}
              </Box>
            </Paper>
          )}
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader 
              title="Recent Executions" 
              action={
                <Button 
                  size="small"
                  onClick={() => navigate(`/executions?agent_id=${id}`)}
                >
                  View All
                </Button>
              }
            />
            <Divider />
            <CardContent sx={{ p: 0 }}>
              {recentExecutions.length > 0 ? (
                <List>
                  {recentExecutions.map(execution => (
                    <React.Fragment key={execution.id}>
                      <ListItem 
                        button
                        onClick={() => navigate(`/executions/${execution.id}`)}
                      >
                        <ListItemText
                          primary={execution.input || 'No input'}
                          secondary={
                            <>
                              <Box component="span">
                                {formatDate(execution.created_at)}
                              </Box>
                              <Box component="span" sx={{ 
                                display: 'inline-block', 
                                ml: 1,
                                px: 1, 
                                py: 0.3,
                                borderRadius: 1,
                                bgcolor: execution.error ? 'warning.light' : 'success.light',
                                color: 'white',
                                fontSize: '0.7rem'
                              }}>
                                {execution.error ? 'Failed' : 'Success'}
                              </Box>
                            </>
                          }
                        />
                      </ListItem>
                      <Divider component="li" />
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    No executions yet
                  </Typography>
                  <Button 
                    variant="contained" 
                    size="small"
                    startIcon={<RunIcon />}
                    onClick={() => setRunDialogOpen(true)}
                    sx={{ mt: 2 }}
                  >
                    Run Agent
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Run Agent Dialog */}
      <Dialog open={runDialogOpen} onClose={() => setRunDialogOpen(false)}>
        <DialogTitle>Run Agent: {agent.name}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="input"
            label="Input"
            type="text"
            fullWidth
            variant="outlined"
            multiline
            rows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={executing}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRunDialogOpen(false)} disabled={executing}>
            Cancel
          </Button>
          <Button 
            onClick={handleRunAgent} 
            variant="contained"
            disabled={executing}
            startIcon={executing ? <CircularProgress size={16} /> : <RunIcon />}
          >
            {executing ? 'Running...' : 'Run'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AgentDetail; 