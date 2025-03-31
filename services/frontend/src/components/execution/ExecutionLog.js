import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Paper, CircularProgress, LinearProgress, Chip } from '@mui/material';
import { styled } from '@mui/material/styles';
import socketService from '../../services/SocketService';
import { useAuth } from '../../contexts/AuthContext';

const LogContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginTop: theme.spacing(2),
  marginBottom: theme.spacing(2),
  maxHeight: '500px',
  overflow: 'auto',
  backgroundColor: '#1e1e1e',
  fontFamily: 'Consolas, monospace',
  color: '#f8f8f8',
  position: 'relative'
}));

const LogEntry = styled(Box)({
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-word',
  fontSize: '0.875rem',
  lineHeight: 1.5,
  paddingLeft: '10px',
  marginBottom: '2px',
  '&.success': { color: '#a8ff60' },
  '&.error': { color: '#ff6b6b' },
  '&.warning': { color: '#ffd700' },
  '&.info': { color: '#6bb9ff' }
});

const StatusChip = styled(Chip)(({ theme, status }) => ({
  marginLeft: theme.spacing(1),
  backgroundColor: 
    status === 'completed' ? theme.palette.success.main :
    status === 'running' ? theme.palette.info.main :
    status === 'failed' ? theme.palette.error.main :
    status === 'cancelled' ? theme.palette.warning.main :
    theme.palette.grey[500],
  color: '#fff'
}));

const ExecutionLog = ({ executionId, initialData = null }) => {
  const { token } = useAuth();
  const [status, setStatus] = useState(initialData?.status || 'queued');
  const [progress, setProgress] = useState(initialData?.progress || 0);
  const [output, setOutput] = useState(initialData?.output || '');
  const [error, setError] = useState(initialData?.error || null);
  const [isConnected, setIsConnected] = useState(false);
  const logContainerRef = useRef(null);

  // Auto-scroll to bottom when output changes
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [output, error]);

  // Connect to socket and listen for execution updates
  useEffect(() => {
    if (!executionId || !token) return;

    // Make sure we're connected to the socket
    if (!socketService.isConnected) {
      socketService.connect(token);
    }
    
    setIsConnected(socketService.isConnected);
    
    // Handle socket connection changes
    const connectHandler = () => setIsConnected(true);
    const disconnectHandler = () => setIsConnected(false);
    
    socketService.on('connect', connectHandler);
    socketService.on('disconnect', disconnectHandler);
    
    // Join the execution room and listen for updates
    const unsubscribe = socketService.joinExecution(executionId, (data) => {
      if (data.status) setStatus(data.status);
      if (data.progress !== undefined) setProgress(data.progress);
      if (data.output) setOutput(data.output);
      if (data.error) setError(data.error);
    });
    
    return () => {
      socketService.off('connect', connectHandler);
      socketService.off('disconnect', disconnectHandler);
      if (unsubscribe) unsubscribe();
    };
  }, [executionId, token]);

  // Parse and format the output
  const renderOutput = () => {
    if (!output) {
      if (status === 'queued') {
        return <LogEntry className="info">Waiting to start execution...</LogEntry>;
      } else if (status === 'running' && progress === 0) {
        return <LogEntry className="info">Initializing execution...</LogEntry>;
      }
      return null;
    }

    return output.split('\n').map((line, index) => {
      // Simple syntax highlighting
      let className = '';
      
      if (line.match(/error|exception|fail/i)) {
        className = 'error';
      } else if (line.match(/warning|warn/i)) {
        className = 'warning';
      } else if (line.match(/info|notice/i)) {
        className = 'info';
      } else if (line.match(/success|completed|done/i)) {
        className = 'success';
      }
      
      return <LogEntry key={index} className={className}>{line}</LogEntry>;
    });
  };

  // Render error
  const renderError = () => {
    if (!error) return null;
    
    return error.split('\n').map((line, index) => (
      <LogEntry key={`error-${index}`} className="error">
        {line}
      </LogEntry>
    ));
  };

  // Get status label
  const getStatusLabel = () => {
    switch (status) {
      case 'queued':
        return 'Queued';
      case 'running':
        return 'Running';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return 'Unknown';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6">
          Execution Log
          <StatusChip
            label={getStatusLabel()}
            status={status}
            size="small"
          />
        </Typography>
        
        {!isConnected && (
          <Chip 
            label="Socket Disconnected" 
            color="error" 
            size="small" 
            sx={{ ml: 1 }}
          />
        )}
      </Box>
      
      {(status === 'queued' || status === 'running') && (
        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ mb: 1, height: 10, borderRadius: 5 }}
        />
      )}
      
      <LogContainer ref={logContainerRef}>
        {status === 'queued' && progress === 0 && !output && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
            <CircularProgress size={24} />
            <Typography variant="body2" sx={{ ml: 2, color: '#6bb9ff' }}>
              Waiting for execution to start...
            </Typography>
          </Box>
        )}
        
        {renderOutput()}
        {renderError()}
        
        {status === 'running' && (
          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
            <CircularProgress size={16} sx={{ mr: 1 }} />
            <Typography variant="body2" sx={{ color: '#6bb9ff' }}>
              Execution in progress...
            </Typography>
          </Box>
        )}
      </LogContainer>
    </Box>
  );
};

export default ExecutionLog; 