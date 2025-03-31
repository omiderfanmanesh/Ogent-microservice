# Command Execution Flow (Database Integration)

## Database Overview

- **MySQL Database**: Used by Auth Service
- **PostgreSQL Database**: Used by Agent Service

## Key Database Interactions

1. **Authentication (MySQL)**
   - Validate user credentials
   - Check user permissions

2. **Command Execution (PostgreSQL)**
   - Create execution record
   - Update status as command progresses
   - Store final results

## Main Tables

### MySQL
- users
- roles
- permissions

### PostgreSQL
- agents
- executions 