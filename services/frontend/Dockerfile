# Stage 1: Build the Vue.js application
FROM node:16-alpine as build-stage

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Ensure the build script exists and runs correctly
RUN npm run build

# Stage 2: Serve the built application with Nginx
FROM nginx:stable-alpine

# Remove default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built Vue.js app from the build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80 (Nginx default)
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]