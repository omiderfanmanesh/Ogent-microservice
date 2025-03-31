#!/bin/bash
set -e

# Color variables
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print with colors
function print_info() {
  echo -e "${GREEN}INFO:${NC} $1"
}

function print_warning() {
  echo -e "${YELLOW}WARNING:${NC} $1"
}

function print_error() {
  echo -e "${RED}ERROR:${NC} $1"
}

# Check for Docker and Docker Compose
if ! command -v docker &> /dev/null; then
  print_error "Docker not found. Please install Docker and try again."
  exit 1
fi

if ! docker compose version &> /dev/null; then
  print_warning "Docker Compose not found or not in PATH."
  print_warning "Trying to use docker-compose instead..."
  
  if ! command -v docker-compose &> /dev/null; then
    print_error "Neither 'docker compose' nor 'docker-compose' was found. Please install Docker Compose and try again."
    exit 1
  fi
  
  COMPOSE_CMD="docker-compose"
else
  COMPOSE_CMD="docker compose"
fi

print_info "Creating .env files from examples..."

# Create .env files from examples for each service
if [ -f "services/api-gateway/.env.example" ]; then
  cp services/api-gateway/.env.example services/api-gateway/.env
  print_info "Created services/api-gateway/.env"
else
  print_warning "services/api-gateway/.env.example not found, skipping..."
fi

if [ -f "services/auth-service/.env.example" ]; then
  cp services/auth-service/.env.example services/auth-service/.env
  print_info "Created services/auth-service/.env"
else
  print_warning "services/auth-service/.env.example not found, skipping..."
fi

if [ -f "services/socket-service/.env.example" ]; then
  cp services/socket-service/.env.example services/socket-service/.env
  print_info "Created services/socket-service/.env"
else
  print_warning "services/socket-service/.env.example not found, skipping..."
fi

if [ -f "services/command-execution/.env.example" ]; then
  cp services/command-execution/.env.example services/command-execution/.env
  print_info "Created services/command-execution/.env"
else
  print_warning "services/command-execution/.env.example not found, skipping..."
fi

print_info "Starting services with Docker Compose..."
$COMPOSE_CMD up -d

# Wait for auth-service to be ready
print_info "Waiting for auth-service to be ready (this may take a while)..."
for i in {1..30}; do
  if $COMPOSE_CMD exec auth-service php artisan --version &> /dev/null; then
    break
  fi
  echo -n "."
  sleep 2
done
echo ""

# Run migrations and seeders
print_info "Running database migrations and seeders..."
$COMPOSE_CMD exec auth-service php artisan migrate --seed

print_info "Setup completed successfully!"
print_info "You can now access the application at http://localhost"
print_info "Default login credentials:"
print_info "  Admin: admin@example.com / admin123"
print_info "  User:  user@example.com / user123"
print_info ""
print_info "To stop all services:"
print_info "  $COMPOSE_CMD down" 