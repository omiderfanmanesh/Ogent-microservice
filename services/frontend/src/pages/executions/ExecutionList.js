import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  DeleteOutline as DeleteIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import apiService from '../../services/api';

const ExecutionList = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  
  // State
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [filters, setFilters] = useState({
    agent_id: queryParams.get('agent_id') || '',
    status: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [agents, setAgents] = useState([]);

  // Fetch executions
  const fetchExecutions = async () => {
    try {
      setLoading(true);
      
      // Apply filters
      const params = {
        offset: page * rowsPerPage,
        limit: rowsPerPage,
        sort: 'created_at:desc'
      };
      
      if (filters.agent_id) params.agent_id = filters.agent_id;
      if (filters.status === 'success') params.error = 'null';
      if (filters.status === 'error') params.error = 'not:null';
      
      const data = await apiService.executions.list(params);
      
      setExecutions(data.items || []);
      setTotalCount(data.total || 0);
      setError(null);
    } catch (err) {
      console.error('Error fetching executions:', err);
      setError('Failed to load executions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch agents for filter
  const fetchAgents = async () => {
    try {
      const data = await apiService.agents.list({ limit: 100 });
      setAgents(data.items || []);
    } catch (err) {
      console.error('Error fetching agents:', err);
    }
  };

  useEffect(() => {
    fetchExecutions();
    fetchAgents();
  }, [page, rowsPerPage]);

  useEffect(() => {
    if (filters.agent_id) {
      // Update URL with agent_id filter
      const newParams = new URLSearchParams(location.search);
      if (filters.agent_id) {
        newParams.set('agent_id', filters.agent_id);
      } else {
        newParams.delete('agent_id');
      }
      navigate({ search: newParams.toString() }, { replace: true });
    }
  }, [filters.agent_id]);

  // Handle page change
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  // Handle rows per page change
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle filter change
  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value
    }));
    setPage(0); // Reset to first page when filters change
    
    // Apply filters immediately
    fetchExecutions();
  };

  // Delete execution
  const handleDeleteExecution = async (id) => {
    if (window.confirm('Are you sure you want to delete this execution?')) {
      try {
        await apiService.executions.delete(id);
        fetchExecutions(); // Refresh the list
      } catch (err) {
        console.error('Error deleting execution:', err);
        setError('Failed to delete execution. Please try again.');
      }
    }
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1">
            Executions
          </Typography>
          
          <Box>
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={() => setShowFilters(!showFilters)}
              sx={{ mr: 1 }}
            >
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={fetchExecutions}
            >
              Refresh
            </Button>
          </Box>
        </Box>
        
        {showFilters && (
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Filters
            </Typography>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel id="agent-filter-label">Agent</InputLabel>
                <Select
                  labelId="agent-filter-label"
                  value={filters.agent_id}
                  name="agent_id"
                  label="Agent"
                  onChange={handleFilterChange}
                >
                  <MenuItem value="">
                    <em>All Agents</em>
                  </MenuItem>
                  {agents.map((agent) => (
                    <MenuItem key={agent.id} value={agent.id}>
                      {agent.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel id="status-filter-label">Status</InputLabel>
                <Select
                  labelId="status-filter-label"
                  value={filters.status}
                  name="status"
                  label="Status"
                  onChange={handleFilterChange}
                >
                  <MenuItem value="">
                    <em>All Statuses</em>
                  </MenuItem>
                  <MenuItem value="success">Success</MenuItem>
                  <MenuItem value="error">Error</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </Paper>
        )}
      </Box>
      
      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}
      
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Agent</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created At</TableCell>
                <TableCell>Input</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                    <CircularProgress size={30} />
                  </TableCell>
                </TableRow>
              ) : executions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                    <Typography variant="body1">No executions found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                executions.map((execution) => (
                  <TableRow key={execution.id} hover>
                    <TableCell 
                      sx={{ 
                        maxWidth: 150, 
                        overflow: 'hidden', 
                        textOverflow: 'ellipsis',
                        cursor: 'pointer' 
                      }}
                      onClick={() => navigate(`/executions/${execution.id}`)}
                    >
                      {execution.id}
                    </TableCell>
                    <TableCell>
                      {execution.agent_name || (
                        execution.agent_id ? (
                          <Box 
                            component="span" 
                            onClick={() => navigate(`/agents/${execution.agent_id}`)}
                            sx={{ 
                              cursor: 'pointer',
                              textDecoration: 'underline',
                              color: 'primary.main'
                            }}
                          >
                            {execution.agent_id.substring(0, 8)}...
                          </Box>
                        ) : 'N/A'
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={execution.error ? 'Error' : 'Success'}
                        color={execution.error ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{formatDate(execution.created_at)}</TableCell>
                    <TableCell 
                      sx={{ 
                        maxWidth: 200, 
                        overflow: 'hidden', 
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      <Tooltip title={execution.input || 'No input'}>
                        <span>{execution.input || 'No input'}</span>
                      </Tooltip>
                    </TableCell>
                    <TableCell align="right">
                      <IconButton 
                        size="small" 
                        onClick={() => navigate(`/executions/${execution.id}`)}
                        color="primary"
                      >
                        <ViewIcon />
                      </IconButton>
                      <IconButton 
                        size="small" 
                        onClick={() => handleDeleteExecution(execution.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          component="div"
          count={totalCount}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
      </Paper>
    </Container>
  );
};

export default ExecutionList; 