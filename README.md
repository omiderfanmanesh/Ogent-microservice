# Ogent - Agent Platform

Ogent is a comprehensive platform for creating, managing, and running autonomous agents. It provides a secure environment for execution of agent actions through a command execution service with a dedicated Ubuntu target.

## Architecture

The platform consists of several microservices:

- **Frontend**: React.js-based UI for interacting with the platform
- **Auth Service**: Laravel-based authentication and authorization service
- **API Gateway**: Routes requests to the appropriate services
- **Socket Service**: Provides real-time communication capabilities
- **Command Execution Service**: Securely executes commands on the target machine
- **Ubuntu Target**: A dedicated Ubuntu environment for running agent commands

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ogent.git
   cd ogent
   ```

2. Create `.env` files from the examples:
   ```bash
   cp services/api-gateway/.env.example services/api-gateway/.env
   cp services/auth-service/.env.example services/auth-service/.env
   cp services/socket-service/.env.example services/socket-service/.env
   cp services/command-execution/.env.example services/command-execution/.env
   ```

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Initialize the database:
   ```bash
   docker-compose exec auth-service php artisan migrate --seed
   ```

### Default Login Credentials

- Admin user: `admin@example.com` / `admin123`
- Regular user: `user@example.com` / `user123`

## Features

- **Authentication**: Secure user authentication and role-based access control
- **Agent Management**: Create, edit, and manage autonomous agents
- **Command Execution**: Execute commands securely on the target machine
- **Real-time Updates**: Get real-time updates on agent executions
- **Role-based Access Control**: Control who can perform what actions

## Testing the Command Execution

1. Log in to the web interface at http://localhost
2. Navigate to "Command" in the main menu
3. Enter a command like `ls -la /tmp` and click Execute
4. View the real-time execution logs

For SSH access to the Ubuntu target (for debugging):
```bash
ssh -p 2222 ubuntu@localhost
```
Password: `ubuntu`

## Development

### Service-specific Development

Each service can be developed independently:

#### Frontend
```bash
cd services/frontend
npm install
npm start
```

#### Auth Service
```bash
cd services/auth-service
composer install
php artisan serve
```

#### Socket Service
```bash
cd services/socket-service
npm install
npm run dev
```

#### Command Execution Service
```bash
cd services/command-execution
pip install -r requirements.txt
python app.py
```

## Security Considerations

- The command execution service only allows a whitelist of commands
- Commands are executed in a sandboxed environment
- Role-based permissions control who can execute commands
- All API requests require authentication

## API Key Management

The platform requires an OpenAI API key to function. For security reasons, never commit API keys to the repository.

### Setting up API Keys

1. Copy the environment example files:
   ```bash
   cp services/langchain-agent/.env.example services/langchain-agent/.env
   ```

2. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. For production, create and modify the production environment file:
   ```bash
   cp .env.prod.example .env.prod
   ```

4. The project uses GPT-4o-mini by default. You can change this in the environment files.

5. The repository's `.gitignore` is configured to exclude all `.env` files except example files, ensuring your API keys stay private.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 