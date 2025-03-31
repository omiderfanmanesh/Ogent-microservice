# Deployment Guide

This guide provides instructions for deploying Ogent in various environments.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [CI/CD Pipelines](#cicd-pipelines)

## Local Development

For local development, refer to the main README.md file's setup instructions.

## Docker Deployment

### Development Environment

For a Docker-based development environment:

```bash
# Use the helper script
./docker.sh up

# Or manually with Docker Compose
docker-compose up -d
```

### Production Environment

For a production Docker deployment:

1. Initialize the production environment:
   ```bash
   ./docker.sh prod-init
   ```

2. Edit the `.env.prod` file with your production settings:
   ```bash
   nano .env.prod
   ```
   
   Make sure to set secure values for:
   - `SECRET_KEY`
   - `POSTGRES_PASSWORD`
   - `ADMIN_PASSWORD`
   - `OPENAI_API_KEY`

3. Start the production services:
   ```bash
   ./docker.sh prod-up
   ```

## Production Deployment

### Prerequisites

- Linux server (Ubuntu 20.04 or newer recommended)
- Docker and Docker Compose installed
- Domain name configured with DNS
- Optional: Nginx or other reverse proxy for SSL termination

### Server Setup

1. Install Docker and Docker Compose:
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ogent.git
   cd ogent
   ```

3. Set up production environment:
   ```bash
   cp .env.prod.example .env.prod
   nano .env.prod  # Edit with your production settings
   ```

4. Start the application:
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

### Reverse Proxy with Nginx

For SSL termination and domain routing, set up Nginx:

1. Install Nginx:
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. Create an Nginx configuration file:
   ```bash
   sudo nano /etc/nginx/sites-available/ogent
   ```

3. Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           return 301 https://$host$request_uri;
       }
   }
   
   server {
       listen 443 ssl;
       server_name yourdomain.com;
       
       ssl_certificate /path/to/certificate.crt;
       ssl_certificate_key /path/to/private.key;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       location /api/v1/executions {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_read_timeout 86400;  # 24 hours for long-lived connections
       }
   }
   ```

4. Enable the site and restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/ogent /etc/nginx/sites-enabled/
   sudo nginx -t  # Test configuration
   sudo systemctl restart nginx
   ```

5. Set up SSL with Let's Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

## CI/CD Pipelines

### GitHub Actions

This project includes a GitHub Actions workflow in `.github/workflows/ci.yml` for:
- Code linting
- Docker image building
- Running tests

To set up continuous deployment:

1. Add the following section to the CI workflow:

```yaml
  deploy:
    needs: [lint, build, test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SSH_HOST }}
        username: ${{ secrets.SSH_USERNAME }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /path/to/ogent
          git pull
          docker-compose -f docker-compose.prod.yml --env-file .env.prod down
          docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

2. Add the necessary secrets in your GitHub repository:
   - `SSH_HOST`: Your server IP or hostname
   - `SSH_USERNAME`: SSH username
   - `SSH_PRIVATE_KEY`: SSH private key for authentication

### GitLab CI/CD

For GitLab deployments, create a `.gitlab-ci.yml` file:

```yaml
stages:
  - lint
  - build
  - test
  - deploy

lint:
  stage: lint
  image: python:3.10
  script:
    - pip install black mypy isort
    - black --check app
    - isort --check-only app
    - mypy app

build:
  stage: build
  image: docker:20.10
  services:
    - docker:20.10-dind
  script:
    - docker build -t ogent:test .
    - docker run --rm ogent:test python -c "import app; print('Image built successfully')"

test:
  stage: test
  image: python:3.10
  services:
    - postgres:14-alpine
  variables:
    POSTGRES_PASSWORD: postgres
    POSTGRES_USER: postgres
    POSTGRES_DB: ogent_test
    DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/ogent_test
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-asyncio
    - cp .env.example .env
    - sed -i 's/postgresql+asyncpg:\/\/postgres:postgres@localhost:5432\/ogent/postgresql+asyncpg:\/\/postgres:postgres@postgres:5432\/ogent_test/g' .env
    - python -m pytest

deploy:
  stage: deploy
  image: alpine:latest
  only:
    - main
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
  script:
    - ssh -o StrictHostKeyChecking=no $SSH_USERNAME@$SSH_HOST "cd /path/to/ogent && git pull && docker-compose -f docker-compose.prod.yml --env-file .env.prod down && docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build"
```

Remember to set up the appropriate CI/CD variables in GitLab. 