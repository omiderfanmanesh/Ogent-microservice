<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;
use Illuminate\Support\Facades\Hash;

class UserRepositoryTest extends TestCase
{
    use RefreshDatabase, WithFaker;

    /**
     * Test that a user can be created
     */
    public function test_user_can_be_created()
    {
        // Create a user
        $userData = [
            'name' => 'Test User',
            'username' => 'testuser' . rand(1000, 9999),
            'email' => $this->faker->unique()->safeEmail(),
            'password' => 'password123',
        ];

        $user = User::create([
            'name' => $userData['name'],
            'username' => $userData['username'],
            'email' => $userData['email'],
            'password' => Hash::make($userData['password']),
        ]);

        // Assert the user was created
        $this->assertInstanceOf(User::class, $user);
        $this->assertEquals($userData['name'], $user->name);
        $this->assertEquals($userData['username'], $user->username);
        $this->assertEquals($userData['email'], $user->email);
        $this->assertTrue(Hash::check($userData['password'], $user->password));
        
        // Assert the user exists in the database
        $this->assertDatabaseHas('users', [
            'name' => $userData['name'],
            'username' => $userData['username'],
            'email' => $userData['email'],
        ]);
    }

    /**
     * Test that a user can be retrieved
     */
    public function test_user_can_be_retrieved()
    {
        // Create a user
        $user = User::factory()->create();
        
        // Retrieve the user
        $retrievedUser = User::find($user->id);
        
        // Assert the user was retrieved
        $this->assertInstanceOf(User::class, $retrievedUser);
        $this->assertEquals($user->id, $retrievedUser->id);
        $this->assertEquals($user->name, $retrievedUser->name);
        $this->assertEquals($user->email, $retrievedUser->email);
    }

    /**
     * Test that a user can be updated
     */
    public function test_user_can_be_updated()
    {
        // Create a user
        $user = User::factory()->create();
        
        // Update user data
        $newName = 'Updated Name';
        $newEmail = 'updated_' . $this->faker->unique()->safeEmail();
        
        $user->name = $newName;
        $user->email = $newEmail;
        $user->save();
        
        // Refresh the user from the database
        $user->refresh();
        
        // Assert the user was updated
        $this->assertEquals($newName, $user->name);
        $this->assertEquals($newEmail, $user->email);
        
        // Assert the updated user exists in the database
        $this->assertDatabaseHas('users', [
            'id' => $user->id,
            'name' => $newName,
            'email' => $newEmail,
        ]);
    }

    /**
     * Test that a user can be deleted
     */
    public function test_user_can_be_deleted()
    {
        // Create a user
        $user = User::factory()->create();
        
        // Delete the user
        $user->delete();
        
        // Assert the user was deleted
        $this->assertDatabaseMissing('users', [
            'id' => $user->id,
        ]);
        
        // Assert the user cannot be retrieved
        $this->assertNull(User::find($user->id));
    }
} 