# Command Execution Flow (PlantUML Format)

```plantuml
@startuml
!theme cerulean
title Ogent Command Execution Flow

actor "User" as user
participant "Frontend\n(React/Nginx)" as frontend
participant "API Gateway\n(Node.js)" as apigateway
participant "Auth Service\n(Laravel)" as authservice
participant "Command Execution\nService (Python)" as cmdservice
participant "Socket Service\n(Node.js)" as socketservice
participant "Ubuntu Target\nContainer" as ubuntu

user -> frontend: Enter command in UI
activate frontend

frontend -> apigateway: POST /api/command\nHeaders: {Authorization: Bearer JWT}\nBody: {command: "ls -la", params: {...}}
activate apigateway

apigateway -> authservice: POST /api/auth/validate\nHeaders: {Authorization: Bearer JWT}
activate authservice
authservice --> apigateway: HTTP 200 OK\n{valid: true, user: {...}, permissions: [...]}
deactivate authservice

alt Invalid Token
    apigateway --> frontend: HTTP 401 Unauthorized
    frontend --> user: Display authentication error
end

apigateway -> cmdservice: POST /api/execute\nHeaders: {Authorization: Bearer JWT}\nBody: {command: "ls -la", userId: "123", params: {...}}
activate cmdservice

cmdservice -> cmdservice: Validate command against whitelist

alt Command Not Allowed
    cmdservice --> apigateway: HTTP 403 Forbidden\n{error: "Command not permitted"}
    apigateway --> frontend: HTTP 403 Forbidden
    frontend --> user: Display permission error
end

cmdservice -> socketservice: Create execution channel\n{executionId: "exec_123", userId: "123"}
activate socketservice
socketservice --> cmdservice: Channel created

cmdservice -> ubuntu: Execute command via SSH
activate ubuntu

frontend -> socketservice: WebSocket Connect\n{executionId: "exec_123", token: JWT}
socketservice --> frontend: Connection established

loop While command executing
    ubuntu --> cmdservice: Command output (streaming)
    cmdservice -> socketservice: Push output\n{executionId: "exec_123", output: "..."}
    socketservice --> frontend: WebSocket message\n{output: "...", status: "running"}
    frontend --> user: Display real-time output
end

ubuntu --> cmdservice: Command completed\n{exitCode: 0, output: "...", execTime: 1200}
deactivate ubuntu

cmdservice -> socketservice: Close channel\n{executionId: "exec_123", status: "completed"}
deactivate socketservice

cmdservice --> apigateway: HTTP 200 OK\n{status: "completed", exitCode: 0, execTime: 1200}
deactivate cmdservice

apigateway --> frontend: HTTP 200 OK\n{status: "completed", exitCode: 0, execTime: 1200}
deactivate apigateway

frontend --> user: Display completion status
deactivate frontend

@enduml
```

This detailed sequence diagram shows the complete flow of a command execution in the Ogent platform, including HTTP methods, headers, payload formats, and error handling paths. The diagram helps visualize how the different services interact during command execution and how data flows through the system. 