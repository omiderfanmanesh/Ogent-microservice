#!/bin/bash

# Check if Laravel is already installed
if [ ! -f "artisan" ]; then
    echo "Creating new Laravel project..."
    composer create-project laravel/laravel . --prefer-dist
    
    # Copy our customized .env file
    cp .env.example .env
    
    # Generate application key
    php artisan key:generate
    
    # Install additional packages
    composer require laravel/sanctum spatie/laravel-permission
    
    echo "Laravel installed successfully!"
else
    echo "Laravel already installed, running migrations..."
fi

# Run migrations
php artisan migrate

echo "Auth service initialization complete!" 