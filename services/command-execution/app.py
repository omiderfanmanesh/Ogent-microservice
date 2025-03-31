from flask import Flask, request, jsonify
import subprocess
import os
import json
import uuid
import time
import threading
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
import jwt
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SOCKET_SERVICE_URL = os.getenv('SOCKET_SERVICE_URL', 'http://socket-service:3002')
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8000/api')
JWT_SECRET = os.getenv('JWT_SECRET', 'default_secret_key')
ALLOWED_COMMANDS_PATH = os.getenv('ALLOWED_COMMANDS_PATH', 'allowed_commands.json')
MAX_EXECUTION_TIME = int(os.getenv('MAX_EXECUTION_TIME', '3600'))  # 1 hour in seconds
EXECUTION_DIR = os.getenv('EXECUTION_DIR', '/tmp/executions')

# Create execution directory if it doesn't exist
os.makedirs(EXECUTION_DIR, exist_ok=True)

# Active executions
active_executions = {}

# Load allowed commands
def load_allowed_commands():
    try:
        if os.path.exists(ALLOWED_COMMANDS_PATH):
            with open(ALLOWED_COMMANDS_PATH, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Allowed commands file not found: {ALLOWED_COMMANDS_PATH}")
            return {
                "commands": ["ls", "echo", "cat", "grep", "find", "pwd"],
                "paths": ["/tmp", "/home", "/usr/bin"]
            }
    except Exception as e:
        logger.error(f"Error loading allowed commands: {str(e)}")
        return {
            "commands": ["ls", "echo"],
            "paths": ["/tmp"]
        }

allowed_commands_config = load_allowed_commands()

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # FOR TESTING: Bypass token verification and set a mock user
        request.user = {
            'id': 1,
            'name': 'Test User',
            'roles': [{
                'name': 'admin',
                'permissions': [{'name': 'run agents'}]
            }]
        }
        return f(*args, **kwargs)
        
        # Original code below - commented out for testing
        """
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token with auth service
        try:
            response = requests.get(
                f"{AUTH_SERVICE_URL}/user",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code != 200:
                return jsonify({'error': 'Invalid token'}), 401
                
            user_data = response.json().get('user', {})
            
            # Check if user has permission to execute commands
            has_permission = False
            for role in user_data.get('roles', []):
                for permission in role.get('permissions', []):
                    if permission.get('name') == 'run agents':
                        has_permission = True
                        break
                if has_permission:
                    break
            
            if not has_permission:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Add user to request context
            request.user = user_data
            
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return jsonify({'error': 'Failed to verify token'}), 401
        """
        
    return decorated

# Validate command against allowed list
def is_command_allowed(command):
    parts = command.split()
    if not parts:
        return False
    
    base_command = parts[0]
    
    # Check if the base command is in the allowed list
    if base_command not in allowed_commands_config.get('commands', []):
        return False
    
    # Check if command tries to access disallowed paths
    for part in parts[1:]:
        if part.startswith('/') or part.startswith('./') or part.startswith('../'):
            path_allowed = False
            for allowed_path in allowed_commands_config.get('paths', []):
                if part.startswith(allowed_path):
                    path_allowed = True
                    break
            if not path_allowed:
                return False
    
    return True

# Execute command in a separate thread
def execute_command_task(execution_id, command, user_id):
    try:
        # Create unique directory for this execution
        execution_path = os.path.join(EXECUTION_DIR, execution_id)
        os.makedirs(execution_path, exist_ok=True)
        
        # Update status - starting
        update_execution_status(execution_id, 'running', 1, "Starting execution...", None)
        
        # Start time
        start_time = time.time()
        
        # Output file
        output_file = os.path.join(execution_path, 'output.txt')
        error_file = os.path.join(execution_path, 'error.txt')
        
        # Run command with timeout
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=execution_path
        )
        
        # Store process in active executions
        active_executions[execution_id] = {
            'process': process,
            'start_time': start_time,
            'user_id': user_id
        }
        
        # Poll process and update status
        output_lines = []
        error_lines = []
        
        while True:
            # Check if process has timed out
            if time.time() - start_time > MAX_EXECUTION_TIME:
                process.kill()
                update_execution_status(
                    execution_id, 
                    'failed', 
                    100, 
                    '\n'.join(output_lines), 
                    "Execution timed out"
                )
                break
            
            # Check if process has completed
            return_code = process.poll()
            if return_code is not None:
                # Process has completed
                stdout, stderr = process.communicate()
                
                # Store output
                output_lines.extend([line for line in stdout.split('\n') if line])
                error_lines.extend([line for line in stderr.split('\n') if line])
                
                with open(output_file, 'w') as f:
                    f.write(stdout)
                
                with open(error_file, 'w') as f:
                    f.write(stderr)
                
                # Update status
                if return_code == 0:
                    update_execution_status(
                        execution_id, 
                        'completed', 
                        100, 
                        '\n'.join(output_lines), 
                        None
                    )
                else:
                    update_execution_status(
                        execution_id, 
                        'failed', 
                        100, 
                        '\n'.join(output_lines), 
                        '\n'.join(error_lines)
                    )
                break
            
            # Process is still running, read output
            stdout_line = process.stdout.readline().strip()
            if stdout_line:
                output_lines.append(stdout_line)
                # Update status with progress
                progress = min(99, int(len(output_lines) / 10))  # Simple progress estimation
                update_execution_status(
                    execution_id, 
                    'running', 
                    progress, 
                    '\n'.join(output_lines[-10:]),  # Last 10 lines
                    None
                )
            
            # Small delay to prevent high CPU usage
            time.sleep(0.1)
        
        # Clean up
        if execution_id in active_executions:
            del active_executions[execution_id]
        
    except Exception as e:
        logger.error(f"Error in execution {execution_id}: {str(e)}")
        update_execution_status(execution_id, 'failed', 100, "", str(e))
        if execution_id in active_executions:
            del active_executions[execution_id]

# Update execution status and notify socket service
def update_execution_status(execution_id, status, progress, output, error):
    try:
        data = {
            'executionId': execution_id,
            'status': status,
            'progress': progress
        }
        
        if output:
            data['output'] = output
        
        if error:
            data['error'] = error
        
        # Send update to socket service
        response = requests.post(f"{SOCKET_SERVICE_URL}/api/execution-status", json=data)
        if response.status_code != 200:
            logger.error(f"Failed to update socket service: {response.text}")
    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/api/execute', methods=['POST'])
@token_required
def execute_command():
    data = request.json
    
    # Validate request
    if not data or 'command' not in data:
        return jsonify({'error': 'Command is required'}), 400
    
    command = data['command']
    
    # Security check - validate command
    if not is_command_allowed(command):
        return jsonify({'error': 'Command not allowed'}), 403
    
    # Generate execution ID
    execution_id = str(uuid.uuid4())
    
    # Start execution in background thread
    execution_thread = threading.Thread(
        target=execute_command_task,
        args=(execution_id, command, request.user['id'])
    )
    execution_thread.daemon = True
    execution_thread.start()
    
    return jsonify({
        'executionId': execution_id,
        'status': 'queued',
        'message': 'Command scheduled for execution'
    })

@app.route('/api/execution/<execution_id>', methods=['GET'])
@token_required
def get_execution_status(execution_id):
    # Check if execution is active
    if execution_id in active_executions:
        execution = active_executions[execution_id]
        
        # Check if user has permission to view this execution
        if str(execution['user_id']) != str(request.user['id']):
            return jsonify({'error': 'Not authorized to view this execution'}), 403
        
        # Check process status
        return_code = execution['process'].poll()
        status = 'running' if return_code is None else ('completed' if return_code == 0 else 'failed')
        
        return jsonify({
            'executionId': execution_id,
            'status': status,
            'startTime': datetime.fromtimestamp(execution['start_time']).isoformat(),
            'elapsedTime': int(time.time() - execution['start_time'])
        })
    
    # Check if execution files exist
    execution_path = os.path.join(EXECUTION_DIR, execution_id)
    if os.path.exists(execution_path):
        output_file = os.path.join(execution_path, 'output.txt')
        error_file = os.path.join(execution_path, 'error.txt')
        
        output = ""
        error = ""
        
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                output = f.read()
        
        if os.path.exists(error_file):
            with open(error_file, 'r') as f:
                error = f.read()
        
        return jsonify({
            'executionId': execution_id,
            'status': 'completed' if not error else 'failed',
            'output': output,
            'error': error
        })
    
    return jsonify({'error': 'Execution not found'}), 404

@app.route('/api/execution/<execution_id>/cancel', methods=['POST'])
@token_required
def cancel_execution(execution_id):
    # Check if execution is active
    if execution_id in active_executions:
        execution = active_executions[execution_id]
        
        # Check if user has permission to cancel this execution
        if str(execution['user_id']) != str(request.user['id']):
            return jsonify({'error': 'Not authorized to cancel this execution'}), 403
        
        # Kill process
        execution['process'].kill()
        
        # Update status
        update_execution_status(
            execution_id, 
            'cancelled', 
            100, 
            "Execution cancelled by user", 
            None
        )
        
        # Remove from active executions
        del active_executions[execution_id]
        
        return jsonify({
            'executionId': execution_id,
            'status': 'cancelled',
            'message': 'Execution cancelled'
        })
    
    return jsonify({'error': 'Execution not found or already completed'}), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 