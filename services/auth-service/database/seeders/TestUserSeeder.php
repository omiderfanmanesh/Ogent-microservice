<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\User;
use Spatie\Permission\Models\Role;
use Illuminate\Support\Facades\Hash;

class TestUserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Create a test user with login info if it doesn't exist
        if (!User::where('email', 'user@example.com')->exists()) {
            $user = User::create([
                'name' => 'Test User',
                'email' => 'user@example.com',
                'username' => 'testuser',
                'password' => Hash::make('password123'),
            ]);
            
            // Give the user role
            $userRole = Role::where('name', 'user')->first();
            if ($userRole) {
                $user->assignRole($userRole);
            }
            
            $this->command->info('Test user created successfully.');
        } else {
            $this->command->info('Test user already exists.');
        }
    }
} 