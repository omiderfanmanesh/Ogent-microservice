# Command Execution Flow (Tabular Format)

| Step | Source | Destination | Data/Payload | Purpose | Response |
|------|--------|-------------|--------------|---------|----------|
| 1 | User | Frontend | Command text input | Initiate command execution | UI feedback (request sent) |
| 2 | Frontend | API Gateway | `POST /api/command`<br>Headers: `{Authorization: Bearer JWT}`<br>Body: `{command: "ls -la", params: {...}}` | Send command request with authentication | - |
| 3 | API Gateway | Auth Service | `POST /api/auth/validate`<br>Headers: `{Authorization: Bearer JWT}` | Validate user token and permissions | `{valid: true, user: {...}, permissions: [...]}` |
| 4 | API Gateway | Command Execution Service | `POST /api/execute`<br>Headers: `{Authorization: Bearer JWT}`<br>Body: `{command: "ls -la", userId: "123", params: {...}}` | Forward validated command request | - |
| 5 | Command Execution Service | Internal | Command string | Validate command against allowed_commands.json | Validation result |
| 6 | Command Execution Service | Socket Service | `{executionId: "exec_123", userId: "123"}` | Create execution channel for real-time updates | Channel confirmation |
| 7 | Frontend | Socket Service | WebSocket Connect<br>`{executionId: "exec_123", token: JWT}` | Establish socket connection for updates | WebSocket connection established |
| 8 | Command Execution Service | Ubuntu Target | SSH command execution | Execute command in isolated environment | Command begins execution |
| 9 | Ubuntu Target | Command Execution Service | Standard output/error streams | Stream command execution results | Output data |
| 10 | Command Execution Service | Socket Service | `{executionId: "exec_123", output: "...", status: "running"}` | Forward real-time output | - |
| 11 | Socket Service | Frontend | WebSocket message<br>`{output: "...", status: "running"}` | Send real-time updates | - |
| 12 | Frontend | User | Formatted output | Display real-time command output | Visual feedback |
| 13 | Ubuntu Target | Command Execution Service | `{exitCode: 0, output: "...", execTime: 1200}` | Signal command completion | - |
| 14 | Command Execution Service | Socket Service | `{executionId: "exec_123", status: "completed", exitCode: 0}` | Signal channel completion | - |
| 15 | Command Execution Service | API Gateway | `HTTP 200 OK`<br>`{status: "completed", exitCode: 0, execTime: 1200}` | Return final command result | - |
| 16 | API Gateway | Frontend | `HTTP 200 OK`<br>`{status: "completed", exitCode: 0, execTime: 1200}` | Forward complete result | - |
| 17 | Frontend | User | Success/error notification + complete output | Inform user of completion | User acknowledgment |

## Error Handling Paths

| Error | Step | Source | Destination | Data/Payload | Result |
|-------|------|--------|-------------|--------------|--------|
| Invalid Token | 3-4 | API Gateway | Frontend | `HTTP 401 Unauthorized`<br>`{error: "Invalid or expired token"}` | Authentication error displayed to user |
| Unauthorized Command | 5-6 | Command Execution Service | API Gateway | `HTTP 403 Forbidden`<br>`{error: "Command not permitted"}` | Permission error displayed to user |
| Command Execution Error | 8-9 | Ubuntu Target | Command Execution Service | `{exitCode: 1, error: "Command failed"}` | Error details streamed to frontend |
| Socket Connection Failed | 7 | Socket Service | Frontend | WebSocket Error | Fallback to polling or error notification |
| Command Timeout | 13 | Command Execution Service | API Gateway | `{status: "timeout", error: "Command exceeded maximum execution time"}` | Timeout notification to user |

This tabular representation provides a comprehensive view of the data flow during command execution, showing exactly what information is exchanged between each component at every step of the process. The error handling paths table shows how the system responds to different failure scenarios. 