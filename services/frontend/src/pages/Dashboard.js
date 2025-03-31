import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardHeader,
  Divider,
  CircularProgress,
  Button,
  Container,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField
} from '@mui/material';
import {
  PersonOutline as PersonIcon,
  Code as CodeIcon,
  PlayArrow as PlayIcon,
  Timeline as TimelineIcon,
  Terminal as TerminalIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const Dashboard = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [agents, setAgents] = useState([{ id: 'ubuntu-agent', name: 'Ubuntu Agent' }]);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [command, setCommand] = useState('');
  const [output, setOutput] = useState('');

  useEffect(() => {
    // Mock data - in a real app, you would fetch this from an API
    const fetchStats = async () => {
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setStats({
          agentCount: 5,
          executionCount: 15,
          activeExecutions: 2,
          recentActivity: [
            { id: 1, type: 'agent_created', name: 'Web Scraper', date: '2023-06-15' },
            { id: 2, type: 'execution_completed', name: 'Data Processor', date: '2023-06-14' },
            { id: 3, type: 'agent_updated', name: 'Email Automation', date: '2023-06-13' },
          ]
        });
        
        setLoading(false);
      } catch (err) {
        setError('Failed to load dashboard data');
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleAgentChange = (event) => {
    setSelectedAgent(event.target.value);
  };

  const handleCommandChange = (event) => {
    setCommand(event.target.value);
  };

  const executeCommand = async () => {
    if (!command.trim()) {
      setError('Please enter a command');
      return;
    }
    
    setLoading(true);
    setError('');
    setOutput('');
    
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_COMMAND_SERVICE_URL}/execute`, 
        {
          command: command,
          target: 'ubuntu',
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      setOutput(response.data.output);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to execute command');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon, color, onClick }) => (
    <Card 
      sx={{ 
        minWidth: 200, 
        cursor: onClick ? 'pointer' : 'default',
        transition: 'transform 0.2s',
        '&:hover': onClick ? { transform: 'translateY(-5px)', boxShadow: 3 } : {}
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Box sx={{ mr: 1, color }}>
            {icon}
          </Box>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error">{error}</Typography>
        <Button variant="contained" onClick={() => window.location.reload()} sx={{ mt: 2 }}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Container>
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Welcome, {user?.name || 'User'}
          </Typography>
          
          <FormControl fullWidth sx={{ mb: 3, mt: 2 }}>
            <InputLabel id="agent-select-label">Select Agent</InputLabel>
            <Select
              labelId="agent-select-label"
              id="agent-select"
              value={selectedAgent}
              label="Select Agent"
              onChange={handleAgentChange}
            >
              {agents.map(agent => (
                <MenuItem key={agent.id} value={agent.id}>
                  {agent.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          {selectedAgent && (
            <Box>
              <TextField
                fullWidth
                label="Enter Command"
                variant="outlined"
                value={command}
                onChange={handleCommandChange}
                sx={{ mb: 2 }}
                placeholder="e.g., ls -la, echo Hello, whoami"
              />
              
              <Button 
                variant="contained" 
                onClick={executeCommand}
                disabled={loading || !command.trim()}
                sx={{ mb: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Execute Command'}
              </Button>
              
              {error && (
                <Typography color="error" sx={{ mb: 2 }}>
                  {error}
                </Typography>
              )}
              
              {output && (
                <Card variant="outlined" sx={{ mt: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Command Output
                    </Typography>
                    <Box 
                      component="pre" 
                      sx={{ 
                        backgroundColor: '#f5f5f5', 
                        p: 2, 
                        borderRadius: 1,
                        overflow: 'auto',
                        maxHeight: '300px'
                      }}
                    >
                      {output}
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default Dashboard; 