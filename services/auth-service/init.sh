#!/bin/bash

# Correct database host and port
DB_HOST=${DB_HOST:-auth-db}
DB_PORT=${DB_PORT:-3306}

# Wait for database
echo "Waiting for database connection at $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do
  echo "Waiting..."
  sleep 1
done
echo "Database connection established"

# Set the working directory
cd /var/www/html

# Check if we have the artisan file
if [ -f "artisan" ]; then
  echo "Found Laravel artisan file"
  
  # Generate application key if not set
  APP_KEY_CURRENT=$(grep '^APP_KEY=' .env | cut -d '=' -f2-)
  if [ -z "$APP_KEY_CURRENT" ] || [ "$APP_KEY_CURRENT" = "base64:" ] || [ "$APP_KEY_CURRENT" = "SomeRandomString" ]; then # Check for empty, default placeholder, or previous error value
    echo "Generating new application key..."
    php artisan key:generate --force
  else
    echo "Application key already set."
  fi

  # Run migrations
  echo "Running database migrations..."
  if php artisan migrate --force; then
    echo "Migrations completed successfully"
  else
    echo "Migrations failed, but continuing..."
  fi

  # Run seeders
  echo "Running database seeders..."
  if php artisan db:seed --force; then
    echo "Database seeding completed successfully"
  else
    echo "Seeding failed, but continuing..."
  fi
else
  echo "Laravel artisan file not found in $(pwd)"
  ls -la
fi

# Start Nginx in the background
echo "Starting Nginx in background..."
nginx &

# Give Nginx/system a moment
sleep 3 # Increased delay slightly

# Explicitly check for /var/run
echo "Checking for /var/run directory..."
ls -ld /var/run

# Start PHP-FPM in the foreground (this will be the main process)
# -F: Force to stay in foreground.
# -R: Allow running as root (needed to create socket/pid, will drop privileges for workers based on pool config)
# -y: Specify the configuration file.
echo "Starting PHP-FPM in foreground with explicit config (allowing root)..."
php-fpm -F -R -y /usr/local/etc/php-fpm.conf 