# Command Execution Flow (Swimlane Diagram)

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   User   │  │ Frontend │  │   API    │  │   Auth   │  │ Command  │  │  Socket  │  │  Ubuntu  │
│          │  │          │  │ Gateway  │  │ Service  │  │  Service │  │ Service  │  │  Target  │
├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤  ├──────────┤
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│  Command │  │          │  │          │  │          │  │          │  │          │  │          │
│   Input  │──┼─────────>│  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │ API POST │  │          │  │          │  │          │  │          │  │          │
│          │  │ Request  │──┼─────────>│  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │ Validate │  │          │  │          │  │          │  │          │
│          │  │          │  │  Token   │──┼─────────>│  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │ Verify   │  │          │  │          │  │          │
│          │  │          │  │          │  │ User     │  │          │  │          │  │          │
│          │  │          │  │          │<─┼──────────│  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │ Forward  │  │          │  │          │  │          │  │          │
│          │  │          │  │ Command  │──┼─────────────┼─────────>│  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │ Validate │  │          │  │          │
│          │  │          │  │          │  │          │  │ Command  │  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │ Create   │  │          │  │          │
│          │  │          │  │          │  │          │  │ Channel  │──┼─────────>│  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │<─┼──────────│  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │ Connect  │  │          │  │          │  │          │  │          │  │          │
│          │  │ WebSocket│──┼─────────────┼─────────────┼──────────┼─>│          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │<─┼─────────────┼─────────────┼──────────┼──│          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │ Execute  │  │          │  │          │
│          │  │          │  │          │  │          │  │ Command  │──┼─────────>│  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │ Process  │
│          │  │          │  │          │  │          │  │          │  │          │  │ Command  │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │<─┼──────────│  │ Stream   │
│          │  │          │  │          │  │          │  │          │  │          │  │ Output   │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │ Stream   │  │          │  │          │
│          │  │          │  │          │  │          │  │ Output   │──┼─────────>│  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │<─┼─────────────┼─────────────┼──────────┼──│ Forward  │  │          │
│          │  │          │  │          │  │          │  │          │  │ Output   │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │<─┼──────────│  │          │  │          │  │          │  │          │  │          │
│ View     │  │ Display  │  │          │  │          │  │          │  │          │  │          │
│ Output   │  │ Output   │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │<─┼──────────│  │ Command  │
│          │  │          │  │          │  │          │  │          │  │          │  │ Complete │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │ Close    │  │          │  │          │
│          │  │          │  │          │  │          │  │ Channel  │──┼─────────>│  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │ Return   │  │          │  │          │
│          │  │          │  │          │<─┼─────────────┼──────────│  │          │  │          │
│          │  │          │  │ Final    │  │          │  │ Results  │  │          │  │          │
│          │  │          │  │ Response │  │          │  │          │  │          │  │          │
│          │  │          │<─┼──────────│  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
│          │<─┼──────────│  │          │  │          │  │          │  │          │  │          │
│ Command  │  │ Display  │  │          │  │          │  │          │  │          │  │          │
│ Complete │  │ Status   │  │          │  │          │  │          │  │          │  │          │
│          │  │          │  │          │  │          │  │          │  │          │  │          │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

This swimlane diagram visually represents the flow of a command execution request through all services in the Ogent platform, showing how responsibilities are distributed across different components and how they work together to process the request.

Key points:
- Each column represents a separate service or component
- Time flows from top to bottom
- Horizontal lines show data transfer between components
- Activities within each lane show what each service is responsible for
- The parallel activities (especially during the streaming phase) demonstrate the real-time nature of the system
``` 