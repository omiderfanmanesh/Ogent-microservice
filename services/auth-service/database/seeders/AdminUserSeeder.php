<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class AdminUserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Check if admin user already exists
        $adminExists = User::where('username', 'admin')->exists();
        
        if (!$adminExists) {
            $admin = User::create([
                'name' => 'Admin User',
                'email' => 'admin@example.com',
                'username' => 'admin',
                'password' => Hash::make('password'),
            ]);

            // Assign admin role if using Spatie Permission
            if (class_exists(\Spatie\Permission\Models\Role::class)) {
                $adminRole = \Spatie\Permission\Models\Role::firstOrCreate(['name' => 'admin']);
                $admin->assignRole($adminRole);
            }
            
            $this->command->info('Admin user created successfully');
        } else {
            $this->command->info('Admin user already exists. Skipping creation.');
        }
    }
} 