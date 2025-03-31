#!/bin/bash

# Wait for database
echo "Waiting for database connection..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database connection established"

# Set the working directory
cd /var/www/html

# Check if we have the artisan file
if [ -f "artisan" ]; then
  echo "Found Laravel artisan file"
  
  # Generate application key if not set
  if [ -z "$APP_KEY" ] || [ "$APP_KEY" = "base64:t7kjBH5IJZcxDV0fDsD4gbhR1gzKTJrk/A5sHUXO+pk=" ]; then
    php artisan key:generate --force
    echo "Generated new application key"
  fi

  # Run migrations
  if php artisan migrate --force; then
    echo "Migrations completed successfully"
  else
    echo "Migrations failed, but continuing..."
  fi

  # Run seeders
  if php artisan db:seed --force; then
    echo "Database seeding completed successfully"
  else
    echo "Seeding failed, but continuing..."
  fi
else
  echo "Laravel artisan file not found in $(pwd)"
  ls -la
fi

# Start PHP-FPM
php-fpm &

# Start Nginx
echo "Starting Nginx..."
nginx -g "daemon off;" 