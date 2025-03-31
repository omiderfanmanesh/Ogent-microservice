<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;
use Spatie\Permission\Models\Role;

class AuthControllerTest extends TestCase
{
    use RefreshDatabase, WithFaker;

    protected $defaultUser;
    protected $defaultPassword = 'password123';

    /**
     * Setup the test environment.
     */
    protected function setUp(): void
    {
        parent::setUp();
        
        // Create roles
        $role = Role::create(['name' => 'user']);
        
        // Create a default user for testing
        $this->defaultUser = User::create([
            'name' => 'Test User',
            'username' => 'testuser',
            'email' => 'test@example.com',
            'password' => bcrypt($this->defaultPassword),
        ]);
        
        $this->defaultUser->assignRole($role);
    }

    /**
     * Test user registration with JWT token
     */
    public function test_user_can_register_and_get_token()
    {
        $userData = [
            'name' => 'New Test User',
            'username' => 'newtestuser',
            'email' => 'newtest@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123',
        ];

        $response = $this->postJson('/api/register', $userData);

        $response->assertStatus(201)
            ->assertJsonStructure([
                'user' => [
                    'id', 'name', 'username', 'email', 'created_at', 'updated_at'
                ],
                'access_token',
                'token_type',
            ]);
            
        // Verify token is in correct format (3 parts with 2 dots)
        $token = $response->json('access_token');
        $this->assertEquals(2, substr_count($token, '.'));
        
        // Verify user was created in database
        $this->assertDatabaseHas('users', [
            'name' => $userData['name'],
            'username' => $userData['username'],
            'email' => $userData['email'],
        ]);
    }

    /**
     * Test user login with JWT token using email
     */
    public function test_user_can_login_with_email_and_get_token()
    {
        $credentials = [
            'email' => $this->defaultUser->email,
            'password' => $this->defaultPassword,
        ];

        $response = $this->postJson('/api/login', $credentials);

        $response->assertStatus(200)
            ->assertJsonStructure([
                'user' => [
                    'id', 'name', 'username', 'email', 'created_at', 'updated_at'
                ],
                'token',
                'token_type',
                'expires_in'
            ]);
            
        // Verify token is in correct format (3 parts with 2 dots)
        $token = $response->json('token');
        $this->assertEquals(2, substr_count($token, '.'));
    }
    
    /**
     * Test user login with JWT token using username
     */
    public function test_user_can_login_with_username_and_get_token()
    {
        $credentials = [
            'username' => $this->defaultUser->username,
            'password' => $this->defaultPassword,
        ];

        $response = $this->postJson('/api/login', $credentials);

        $response->assertStatus(200)
            ->assertJsonStructure([
                'user' => [
                    'id', 'name', 'username', 'email', 'created_at', 'updated_at'
                ],
                'token',
                'token_type',
                'expires_in'
            ]);
    }
    
    /**
     * Test protected user route with JWT token
     */
    public function test_user_can_access_protected_route_with_token()
    {
        // Login to get token
        $response = $this->postJson('/api/login', [
            'email' => $this->defaultUser->email,
            'password' => $this->defaultPassword,
        ]);
        
        $token = $response->json('token');
        
        // Test accessing protected route
        $response = $this->withHeaders([
            'Authorization' => 'Bearer ' . $token,
        ])->getJson('/api/user');
        
        $response->assertStatus(200)
            ->assertJsonStructure([
                'user' => [
                    'id', 'name', 'username', 'email'
                ]
            ]);
    }

    /**
     * Test token refresh
     */
    public function test_token_can_be_refreshed()
    {
        // Login to get token
        $response = $this->postJson('/api/login', [
            'email' => $this->defaultUser->email,
            'password' => $this->defaultPassword,
        ]);
        
        $token = $response->json('token');
        
        // Refresh token
        $response = $this->withHeaders([
            'Authorization' => 'Bearer ' . $token,
        ])->postJson('/api/refresh');
        
        $response->assertStatus(200)
            ->assertJsonStructure([
                'user',
                'token',
                'token_type',
                'expires_in'
            ]);
            
        // Verify new token is different from old token
        $newToken = $response->json('token');
        $this->assertNotEquals($token, $newToken);
    }
    
    /**
     * Test token verification for inter-service communication
     */
    public function test_token_verification()
    {
        // Login to get token
        $response = $this->postJson('/api/login', [
            'email' => $this->defaultUser->email,
            'password' => $this->defaultPassword,
        ]);
        
        $token = $response->json('token');
        
        // Verify token
        $response = $this->withHeaders([
            'Authorization' => 'Bearer ' . $token,
        ])->postJson('/api/verify');
        
        $response->assertStatus(200)
            ->assertJson([
                'valid' => true,
            ])
            ->assertJsonStructure([
                'valid',
                'user',
                'roles',
                'permissions'
            ]);
    }
    
    /**
     * Test logout
     */
    public function test_user_can_logout()
    {
        // Login to get token
        $response = $this->postJson('/api/login', [
            'email' => $this->defaultUser->email,
            'password' => $this->defaultPassword,
        ]);
        
        $token = $response->json('token');
        
        // Logout
        $response = $this->withHeaders([
            'Authorization' => 'Bearer ' . $token,
        ])->postJson('/api/logout');
        
        $response->assertStatus(200)
            ->assertJson([
                'message' => 'Successfully logged out',
            ]);
            
        // NOTE: In the current implementation, the JWT token is invalidated via the blacklist
        // but this test is running in-memory, so we can't properly test blacklist functionality here.
        // In a real environment, the token would be invalidated.
    }
    
    /**
     * Test invalid credentials
     */
    public function test_login_with_invalid_credentials_fails()
    {
        $credentials = [
            'email' => $this->defaultUser->email,
            'password' => 'wrong_password',
        ];

        $response = $this->postJson('/api/login', $credentials);

        $response->assertStatus(422);
    }
    
    /**
     * Test protected route without token
     */
    public function test_accessing_protected_route_without_token_fails()
    {
        $response = $this->getJson('/api/user');
        
        $response->assertStatus(401);
    }
} 