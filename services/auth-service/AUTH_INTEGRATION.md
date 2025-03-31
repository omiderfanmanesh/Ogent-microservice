# Auth Service Integration Guide

This guide explains how to integrate your microservice with the Ogent authentication service.

## Using JWT Tokens for Authentication

The Auth Service provides JWT (JSON Web Token) based authentication for secure communication between microservices.

### JWT Benefits for Microservices

- **Stateless**: Tokens contain all necessary information, eliminating the need for session storage
- **Self-contained**: Tokens include user information, roles, and permissions
- **Secure**: Tokens are signed to prevent tampering
- **Efficient**: Minimal database lookups required for verification

## Integration Options

### Option 1: Direct HTTP Verification (Recommended)

Use the Auth Service's `/verify` endpoint to validate tokens and retrieve user information:

```php
// Example using Laravel's HTTP client
use Illuminate\Support\Facades\Http;

$response = Http::withToken($token)
    ->post('http://auth-service/api/verify');

if ($response->successful()) {
    $data = $response->json();
    $isValid = $data['valid'];
    $user = $data['user'];
    $roles = $data['roles'];
    $permissions = $data['permissions'];
    
    // Proceed with your logic
}
```

### Option 2: Using the Auth Client Service

We've created a reusable client service that you can include in your microservice:

1. Copy the `AuthClientService.php` file to your project
2. Use it to verify tokens and check permissions:

```php
use App\Services\AuthClientService;

// Create client (defaults to http://auth-service:80/api)
$authClient = new AuthClientService();

// Verify a token
$userData = $authClient->verifyToken($token);

// Check for a permission
if ($authClient->hasPermission($token, 'create_agents')) {
    // User has the permission
}

// Check for a role
if ($authClient->hasRole($token, 'admin')) {
    // User has the admin role
}
```

### Option 3: JWT Verification Library

For services that don't need to communicate with the Auth Service, you can verify tokens locally:

1. Add the JWT package to your service:
   ```
   composer require php-open-source-saver/jwt-auth
   ```

2. Configure it with the same secret key as the Auth Service:
   ```
   JWT_SECRET=your_shared_secret_key
   ```

3. Use the library to decode and verify tokens:
   ```php
   use PHPOpenSourceSaver\JWTAuth\Facades\JWTAuth;
   
   try {
       $payload = JWTAuth::parseToken()->getPayload();
       $userData = $payload->get('sub'); // User ID
       $roles = $payload->get('roles');
       $permissions = $payload->get('permissions');
   } catch (\Exception $e) {
       // Token is invalid
   }
   ```

## Token Structure

The JWT tokens from the Auth Service contain:

- **sub**: The user ID
- **iat**: Issued at timestamp
- **exp**: Expiration timestamp
- **roles**: Array of user role names
- **permissions**: Array of user permission names

## Security Best Practices

1. **Always use HTTPS** for communication between services
2. **Validate token expiration** before trusting the contents
3. **Check required permissions** for each protected action
4. **Regenerate tokens** when security context changes
5. **Keep JWT secrets secure** and rotate them periodically 