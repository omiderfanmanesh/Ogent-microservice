#!/bin/bash

# Copy the configuration file to the container
docker cp nginx_config.txt ogent-nginx:/etc/nginx/conf.d/default.conf

# Reload Nginx
docker exec ogent-nginx nginx -s reload

echo "Nginx configuration updated and reloaded" 