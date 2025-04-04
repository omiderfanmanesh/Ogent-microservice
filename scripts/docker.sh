#!/bin/bash
#
# Helper script for Docker operations with Ogent Microservices
#

set -e

# Terminal colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage information
show_usage() {
  echo -e "${YELLOW}Ogent Microservices Docker Helper${NC}"
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  build       Build all Docker images"
  echo "  build <service> Build a specific service Docker image (e.g. api-gateway)"
  echo "  up          Start all services in development mode"
  echo "  down        Stop all services"
  echo "  logs        Show logs from all services"
  echo "  logs <service> Show logs from a specific service"
  echo "  shell <service> Start a shell in the specified service container"
  echo "  restart     Restart all services"
  echo "  restart <service> Restart a specific service"
  echo "  db-shell    Start a shell for the database services"
  echo "  prod-init   Initialize production environment"
  echo "  prod-up     Start all services in production mode"
  echo "  prod-down   Stop production services"
  echo ""
  echo "Examples:"
  echo "  $0 up              # Start all services for development"
  echo "  $0 logs api-gateway # Show logs for the API Gateway service"
  echo "  $0 prod-up         # Start all services for production"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
  echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
  exit 1
fi

# Check for Docker Compose command (newer versions use docker compose)
if docker compose version &> /dev/null; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
  COMPOSE_CMD="docker-compose"
else
  echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose first.${NC}"
  exit 1
fi

# Ensure OPENAI_API_KEY environment variable is set for 'up' command
ensure_api_key() {
  if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY environment variable is not set.${NC}"
    echo -e "You can set it with: ${GREEN}export OPENAI_API_KEY=your-key-here${NC}"
    
    # Prompt for API key
    read -p "Would you like to enter your OpenAI API key now? (y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
      read -p "Enter your OpenAI API key: " api_key
      export OPENAI_API_KEY="$api_key"
      echo -e "${GREEN}API key set for this session.${NC}"
    else
      echo -e "${YELLOW}Continuing without API key. Some features may not work correctly.${NC}"
    fi
  fi
}

# Initialize production environment
init_production() {
  if [ -f ".env.prod" ]; then
    echo -e "${YELLOW}Production environment file (.env.prod) already exists.${NC}"
    read -p "Do you want to overwrite it? (y/n): " answer
    if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
      echo -e "${GREEN}Keeping existing .env.prod file.${NC}"
      return
    fi
  fi
  
  cp .env.prod.example .env.prod
  
  echo -e "${GREEN}Created .env.prod from template.${NC}"
  echo -e "${YELLOW}Please edit .env.prod with your production settings before running 'prod-up'.${NC}"
  echo -e "${YELLOW}Especially update SECRET_KEY, database passwords, and admin passwords with secure values.${NC}"
  
  # Generate a secure random key for SECRET_KEY
  if command -v openssl &> /dev/null; then
    RANDOM_KEY=$(openssl rand -hex 32)
    sed -i.bak "s/replace-with-secure-random-key/$RANDOM_KEY/g" .env.prod
    rm -f .env.prod.bak  # Remove backup file
    echo -e "${GREEN}Generated secure random key for SECRET_KEY.${NC}"
  else
    echo -e "${YELLOW}OpenSSL not found. Please manually update SECRET_KEY in .env.prod with a secure random value.${NC}"
  fi
}

# Command dispatcher
case "$1" in
  "build")
    if [ -n "$2" ]; then
      echo -e "${GREEN}Building Ogent $2 service Docker image...${NC}"
      $COMPOSE_CMD build $2
    else
      echo -e "${GREEN}Building all Ogent service Docker images...${NC}"
      $COMPOSE_CMD build
    fi
    ;;
    
  "up")
    ensure_api_key
    echo -e "${GREEN}Starting Ogent microservices (development mode)...${NC}"
    $COMPOSE_CMD up -d
    echo -e "${GREEN}Services started! Access the application at http://localhost:8080${NC}"
    ;;
    
  "down")
    echo -e "${GREEN}Stopping Ogent microservices...${NC}"
    $COMPOSE_CMD down
    echo -e "${GREEN}Services stopped.${NC}"
    ;;
    
  "logs")
    if [ -n "$2" ]; then
      echo -e "${GREEN}Showing logs for $2 service (Ctrl+C to exit)...${NC}"
      if [ "$3" == "prod" ]; then
        $COMPOSE_CMD -f docker-compose.prod.yml logs -f $2
      else
        $COMPOSE_CMD logs -f $2
      fi
    else
      echo -e "${GREEN}Showing logs for all services (Ctrl+C to exit)...${NC}"
      if [ "$2" == "prod" ]; then
        $COMPOSE_CMD -f docker-compose.prod.yml logs -f
      else
        $COMPOSE_CMD logs -f
      fi
    fi
    ;;
    
  "shell")
    if [ -z "$2" ]; then
      echo -e "${RED}Error: You must specify a service name for shell access.${NC}"
      echo -e "${YELLOW}Example: $0 shell api-gateway${NC}"
      exit 1
    fi
    
    echo -e "${GREEN}Starting shell in $2 container...${NC}"
    if [ "$3" == "prod" ]; then
      $COMPOSE_CMD -f docker-compose.prod.yml exec $2 bash || $COMPOSE_CMD -f docker-compose.prod.yml exec $2 sh
    else
      $COMPOSE_CMD exec $2 bash || $COMPOSE_CMD exec $2 sh
    fi
    ;;
    
  "restart")
    if [ -n "$2" ]; then
      echo -e "${GREEN}Restarting $2 service...${NC}"
      if [ "$3" == "prod" ]; then
        $COMPOSE_CMD -f docker-compose.prod.yml restart $2
      else
        $COMPOSE_CMD restart $2
      fi
      echo -e "${GREEN}$2 service restarted.${NC}"
    else
      echo -e "${GREEN}Restarting all services...${NC}"
      if [ "$2" == "prod" ]; then
        $COMPOSE_CMD -f docker-compose.prod.yml restart
      else
        $COMPOSE_CMD restart
      fi
      echo -e "${GREEN}All services restarted.${NC}"
    fi
    ;;
    
  "db-shell")
    echo -e "${GREEN}Available database services:${NC}"
    echo "1. PostgreSQL (agent-service database)"
    echo "2. MySQL (auth-service database)"
    read -p "Choose a database (1-2): " db_choice
    
    if [ "$db_choice" == "1" ]; then
      echo -e "${GREEN}Starting PostgreSQL shell...${NC}"
      if [ "$2" == "prod" ]; then
        $COMPOSE_CMD -f docker-compose.prod.yml exec db psql -U postgres -d langchain_agent
      else
        $COMPOSE_CMD exec db psql -U postgres -d langchain_agent
      fi
    elif [ "$db_choice" == "2" ]; then
      echo -e "${GREEN}Starting MySQL shell...${NC}"
      if [ "$2" == "prod" ]; then
        $COMPOSE_CMD -f docker-compose.prod.yml exec auth-db mysql -u ogent -p ogent_auth
      else
        $COMPOSE_CMD exec auth-db mysql -u ogent -p ogent_auth
      fi
    else
      echo -e "${RED}Invalid choice.${NC}"
    fi
    ;;
    
  "prod-init")
    echo -e "${GREEN}Initializing production environment...${NC}"
    init_production
    ;;
    
  "prod-up")
    if [ ! -f ".env.prod" ]; then
      echo -e "${RED}Error: Production environment file (.env.prod) not found.${NC}"
      echo -e "${YELLOW}Run './docker.sh prod-init' first to create it.${NC}"
      exit 1
    fi
    
    echo -e "${GREEN}Starting Ogent microservices (production mode)...${NC}"
    $COMPOSE_CMD -f docker-compose.prod.yml --env-file .env.prod up -d
    echo -e "${GREEN}Services started! Access the application at http://localhost:8000${NC}"
    ;;
    
  "prod-down")
    echo -e "${GREEN}Stopping production services...${NC}"
    $COMPOSE_CMD -f docker-compose.prod.yml --env-file .env.prod down
    echo -e "${GREEN}Production services stopped.${NC}"
    ;;
    
  *)
    show_usage
    ;;
esac 