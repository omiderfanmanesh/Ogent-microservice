#!/bin/bash

# Create the updated configuration
cat > updated_nginx.conf << 'EOL'
server {
    listen 80;
    server_name localhost;

    # Frontend
    location / {
        proxy_pass http://ogent-frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Authentication Service
    location /auth/ {
        proxy_pass http://ogent-auth-service:80/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API Gateway
    location /api/ {
        proxy_pass http://ogent-api-gateway:8080/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Socket Service - HTTP endpoints
    location /socket-http/ {
        proxy_pass http://ogent-socket-service:3002/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Socket Service - WebSocket
    location /socket/ {
        proxy_pass http://ogent-socket-service:3002/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Command Execution Service
    location /command/ {
        proxy_pass http://ogent-command-execution:5000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Agent Service - using correct container name
    location /agents/ {
        proxy_pass http://ogent-agent-service-test:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Health checks
    location /health {
        access_log off;
        return 200 "OK";
    }

    # Max body size for file uploads
    client_max_body_size 10M;
}
EOL

# Copy the configuration to the Nginx container
docker cp updated_nginx.conf ogent-nginx:/etc/nginx/conf.d/default.conf

# Restart Nginx to apply changes
docker restart ogent-nginx

echo "Nginx configuration updated and Nginx restarted" 