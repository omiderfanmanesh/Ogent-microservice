import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  InputAdornment,
  Paper,
  Divider
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Clear as ClearIcon,
  History as HistoryIcon,
  ContentCopy as CopyIcon
} from '@mui/icons-material';
import commandService from '../../services/CommandService';
import { useAuth } from '../../contexts/AuthContext';
import ExecutionLog from './ExecutionLog';

const CommandExecutor = () => {
  const { token } = useAuth();
  const [command, setCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState([]);
  const [executionId, setExecutionId] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  const handleCommandChange = (e) => {
    setCommand(e.target.value);
    setError(null);
  };

  const handleClearCommand = () => {
    setCommand('');
    setError(null);
  };

  const handleExecuteCommand = async () => {
    if (!command.trim()) {
      setError('Please enter a command');
      return;
    }

    try {
      setIsExecuting(true);
      setError(null);

      const result = await commandService.executeCommand(command, token);
      
      // Add command to history
      setCommandHistory(prev => [
        { command, timestamp: new Date().toISOString(), executionId: result.executionId },
        ...prev.slice(0, 9) // Keep only the last 10 commands
      ]);
      
      // Set execution ID to show logs
      setExecutionId(result.executionId);
      
    } catch (err) {
      setError(err.message || 'Failed to execute command');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleHistoryItemClick = (historyCommand) => {
    setCommand(historyCommand.command);
    setShowHistory(false);
  };

  const handleCopyCommand = (commandText) => {
    navigator.clipboard.writeText(commandText);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleExecuteCommand();
    }
  };

  return (
    <Box>
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Command Execution
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <TextField
              fullWidth
              label="Enter command"
              placeholder="e.g. ls -la /tmp"
              variant="outlined"
              value={command}
              onChange={handleCommandChange}
              onKeyDown={handleKeyDown}
              disabled={isExecuting}
              error={!!error}
              helperText={error}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">$</InputAdornment>
                ),
                endAdornment: command && (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="clear command"
                      onClick={handleClearCommand}
                      edge="end"
                    >
                      <ClearIcon />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<PlayIcon />}
              onClick={handleExecuteCommand}
              disabled={isExecuting || !command.trim()}
            >
              Execute
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<HistoryIcon />}
              onClick={() => setShowHistory(!showHistory)}
            >
              History
            </Button>
          </Box>
          
          {showHistory && commandHistory.length > 0 && (
            <Paper 
              variant="outlined" 
              sx={{ 
                mt: 2, 
                maxHeight: '200px', 
                overflow: 'auto',
                p: 1
              }}
            >
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
                Command History
              </Typography>
              <Divider sx={{ mb: 1 }} />
              
              {commandHistory.map((item, index) => (
                <Box 
                  key={index}
                  sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    py: 0.5,
                    '&:hover': { bgcolor: 'action.hover' },
                    borderRadius: 1,
                    px: 1
                  }}
                >
                  <Box 
                    sx={{ 
                      cursor: 'pointer',
                      flex: 1,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}
                    onClick={() => handleHistoryItemClick(item)}
                  >
                    <Typography variant="body2" component="span" sx={{ fontWeight: 'bold' }}>
                      {item.command}
                    </Typography>
                    <Typography variant="caption" component="span" sx={{ ml: 1, color: 'text.secondary' }}>
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </Typography>
                  </Box>
                  
                  <Box>
                    <IconButton 
                      size="small" 
                      onClick={() => handleCopyCommand(item.command)}
                      title="Copy command"
                    >
                      <CopyIcon fontSize="small" />
                    </IconButton>
                    
                    {item.executionId === executionId ? (
                      <Chip 
                        label="Current" 
                        size="small" 
                        color="primary"
                        sx={{ ml: 1 }}
                      />
                    ) : (
                      <Chip
                        label="View"
                        size="small"
                        variant="outlined"
                        sx={{ ml: 1 }}
                        onClick={() => setExecutionId(item.executionId)}
                      />
                    )}
                  </Box>
                </Box>
              ))}
            </Paper>
          )}
        </CardContent>
      </Card>
      
      {executionId && (
        <ExecutionLog executionId={executionId} />
      )}
    </Box>
  );
};

export default CommandExecutor; 