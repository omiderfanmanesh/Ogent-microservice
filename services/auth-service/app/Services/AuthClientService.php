<?php

namespace App\Services;

use Illuminate\Http\Client\PendingRequest;
use Illuminate\Support\Facades\Http;

class AuthClientService
{
    protected PendingRequest $client;
    protected string $baseUrl;

    public function __construct(string $baseUrl = null)
    {
        $this->baseUrl = $baseUrl ?? env('AUTH_SERVICE_URL', 'http://auth-service:80/api');
        $this->client = Http::baseUrl($this->baseUrl)
            ->acceptJson()
            ->timeout(30);
    }

    /**
     * Verify a JWT token with the auth service
     *
     * @param string $token
     * @return array|null
     */
    public function verifyToken(string $token): ?array
    {
        try {
            $response = $this->client
                ->withToken($token)
                ->post('/verify');

            if ($response->successful()) {
                return $response->json();
            }
            
            return null;
        } catch (\Exception $e) {
            return null;
        }
    }

    /**
     * Get user permissions from a token
     *
     * @param string $token
     * @return array
     */
    public function getPermissions(string $token): array
    {
        $tokenData = $this->verifyToken($token);
        
        if (!$tokenData || !$tokenData['valid']) {
            return [];
        }
        
        return $tokenData['permissions'] ?? [];
    }

    /**
     * Check if a token has a specific permission
     *
     * @param string $token
     * @param string $permission
     * @return bool
     */
    public function hasPermission(string $token, string $permission): bool
    {
        $permissions = $this->getPermissions($token);
        
        return in_array($permission, $permissions);
    }

    /**
     * Get user roles from a token
     *
     * @param string $token
     * @return array
     */
    public function getRoles(string $token): array
    {
        $tokenData = $this->verifyToken($token);
        
        if (!$tokenData || !$tokenData['valid']) {
            return [];
        }
        
        return $tokenData['roles'] ?? [];
    }

    /**
     * Check if a token has a specific role
     *
     * @param string $token
     * @param string $role
     * @return bool
     */
    public function hasRole(string $token, string $role): bool
    {
        $roles = $this->getRoles($token);
        
        return in_array($role, $roles);
    }
} 