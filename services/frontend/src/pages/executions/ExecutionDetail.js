import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  Divider,
  Chip,
  CircularProgress,
  Link
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import apiService from '../../services/api';

const ExecutionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [execution, setExecution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchExecutionData = async () => {
    try {
      setLoading(true);
      const executionData = await apiService.executions.getById(id);
      setExecution(executionData);
      setError(null);
    } catch (err) {
      console.error('Error fetching execution data:', err);
      setError('Failed to load execution data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExecutionData();
  }, [id]);

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getStatusChip = (execution) => {
    if (!execution) return null;
    
    const color = execution.error ? 'error' : 'success';
    const label = execution.error ? 'Failed' : 'Success';
    
    return (
      <Chip
        label={label}
        color={color}
        size="small"
      />
    );
  };

  const getDuration = (start, end) => {
    if (!start || !end) return 'N/A';
    
    const startTime = new Date(start).getTime();
    const endTime = new Date(end).getTime();
    const durationMs = endTime - startTime;
    
    if (durationMs < 1000) {
      return `${durationMs}ms`;
    } else if (durationMs < 60000) {
      return `${(durationMs / 1000).toFixed(2)}s`;
    } else {
      const minutes = Math.floor(durationMs / 60000);
      const seconds = ((durationMs % 60000) / 1000).toFixed(0);
      return `${minutes}m ${seconds}s`;
    }
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
          onClick={() => navigate('/executions')}
          sx={{ mt: 2 }}
        >
          Back to Executions
        </Button>
      </Container>
    );
  }

  if (!execution) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography>Execution not found</Typography>
        <Button 
          variant="outlined" 
          startIcon={<BackIcon />}
          onClick={() => navigate('/executions')}
          sx={{ mt: 2 }}
        >
          Back to Executions
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
          onClick={() => navigate('/executions')}
          sx={{ mb: 2 }}
        >
          Back to Executions
        </Button>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1">
            Execution Details
            <Box component="span" sx={{ ml: 2 }}>
              {getStatusChip(execution)}
            </Box>
          </Typography>
          
          <Box>
            <Button 
              variant="outlined" 
              startIcon={<RefreshIcon />}
              onClick={fetchExecutionData}
            >
              Refresh
            </Button>
          </Box>
        </Box>
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Execution Summary
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Execution ID
                </Typography>
                <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>
                  {execution.id}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Agent
                </Typography>
                <Typography variant="body1">
                  {execution.agent_id ? (
                    <Link 
                      component="button"
                      variant="body1"
                      onClick={() => navigate(`/agents/${execution.agent_id}`)}
                    >
                      {execution.agent_name || execution.agent_id}
                    </Link>
                  ) : 'N/A'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Started At
                </Typography>
                <Typography variant="body1">
                  {formatDate(execution.created_at)}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Duration
                </Typography>
                <Typography variant="body1">
                  {getDuration(execution.created_at, execution.updated_at)}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
          
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Input
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box component="pre" sx={{ 
              p: 2, 
              bgcolor: 'grey.100', 
              borderRadius: 1,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}>
              {execution.input || 'No input provided'}
            </Box>
          </Paper>
          
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Output
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box component="pre" sx={{ 
              p: 2, 
              bgcolor: 'grey.100', 
              borderRadius: 1,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}>
              {execution.output || 'No output generated'}
            </Box>
          </Paper>
          
          {execution.error && (
            <Paper sx={{ p: 3, bgcolor: 'error.light' }}>
              <Typography variant="h6" gutterBottom sx={{ color: 'error.contrastText' }}>
                Error
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Box component="pre" sx={{ 
                p: 2, 
                bgcolor: 'rgba(0,0,0,0.1)', 
                borderRadius: 1,
                color: 'error.contrastText',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}>
                {execution.error}
              </Box>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default ExecutionDetail; 