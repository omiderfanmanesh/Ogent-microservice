FROM php:8.2-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libssl-dev \
    libzip-dev \
    zip \
    unzip \
    libpq-dev \
    nginx \
    netcat-openbsd

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
# Changed approach to avoid tokenizer issue
RUN docker-php-ext-configure gd && \
    docker-php-ext-install -j$(nproc) \
    pdo \
    pdo_mysql \
    pdo_pgsql \
    mbstring \
    exif \
    pcntl \
    bcmath \
    gd \
    xml \
    zip

# Get latest Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Create a temp directory for Laravel installation
WORKDIR /tmp
RUN composer create-project --prefer-dist laravel/laravel:^10.0 laravel --no-interaction && \
    cd laravel && \
    composer require laravel/sanctum spatie/laravel-permission

# Set up the final directory
WORKDIR /var/www/html

# Remove any existing files
RUN rm -rf /var/www/html/*

# Copy the Laravel project to the final directory
RUN cp -r /tmp/laravel/. /var/www/html/ && \
    rm -rf /tmp/laravel

# Copy custom files over the Laravel installation
COPY . /var/www/html/

# Configure PHP-FPM to use Unix socket
COPY www-socket.conf /usr/local/etc/php-fpm.d/www-socket.conf

# Ensure /var/run exists and is writable by www-data for the socket
RUN mkdir -p /var/run && chown www-data:www-data /var/run

# Configure Nginx
COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/

# Make initialization script executable
RUN chmod +x init.sh

# Set permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html/storage \
    && chmod -R 755 /var/www/html/bootstrap/cache

# Expose port 80
EXPOSE 80

# Set entry point
CMD ["/var/www/html/init.sh"] 